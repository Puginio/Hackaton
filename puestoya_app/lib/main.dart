import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:url_launcher/url_launcher.dart';

// CAMBIA ESTA URL POR LA DE TU BACKEND PYTHON (ej. http://192.168.1.70:8000 o https://tu-url.ngrok-free.app)
const String backendUrl = "http://192.168.158.226:8000";

void main() {
  runApp(const PuestoYaApp());
}

class PuestoYaApp extends StatelessWidget {
  const PuestoYaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PuestoYa',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1E88E5)),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('PuestoYa 🛠️', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Theme.of(context).colorScheme.primaryContainer,
      ),
      body: _selectedIndex == 0 ? const TrabajadorTab() : const VecinoTab(),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: (idx) => setState(() => _selectedIndex = idx),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.engineering), label: 'Soy Trabajador'),
          NavigationDestination(icon: Icon(Icons.search), label: 'Busco Servicio'),
        ],
      ),
    );
  }
}

// ==================== PESTAÑA 1: TRABAJADOR (VOZ + FOTO -> CV) ====================
class TrabajadorTab extends StatefulWidget {
  const TrabajadorTab({super.key});

  @override
  State<TrabajadorTab> createState() => _TrabajadorTabState();
}

class _TrabajadorTabState extends State<TrabajadorTab> {
  final TextEditingController _textoCtrl = TextEditingController();
  final stt.SpeechToText _speech = stt.SpeechToText();
  bool _escuchando = false;
  bool _cargando = false;
  File? _foto;
  Map<String, dynamic>? _cvGenerado;

  Future<void> _toggleVoz() async {
    if (!_escuchando) {
      bool disponible = await _speech.initialize();
      if (disponible) {
        setState(() => _escuchando = true);
        _speech.listen(
          localeId: 'es_MX',
          onResult: (res) {
            setState(() {
              _textoCtrl.text = res.recognizedWords;
            });
          },
        );
      }
    } else {
      await _speech.stop();
      setState(() => _escuchando = false);
    }
  }

  Future<void> _tomarFoto() async {
    final picker = ImagePicker();
    final picked = await picker.pickImage(source: ImageSource.camera, imageQuality: 70);
    if (picked != null) {
      setState(() => _foto = File(picked.path));
    }
  }

  Future<void> _enviarPerfil() async {
    if (_textoCtrl.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Habla o escribe tu oficio, zona y teléfono primero')),
      );
      return;
    }

    setState(() {
      _cargando = true;
      _cvGenerado = null;
    });

    try {
      var request = http.MultipartRequest('POST', Uri.parse('$backendUrl/procesar-trabajador'));
      request.fields['texto'] = _textoCtrl.text;
      if (_foto != null) {
        request.files.add(await http.MultipartFile.fromPath('foto', _foto!.path));
      }

      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        setState(() {
          _cvGenerado = jsonDecode(utf8.decode(response.bodyBytes));
        });
      } else {
        throw Exception('Error del servidor: ${response.statusCode}');
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al conectar con backend: $e')),
      );
    } finally {
      setState(() => _cargando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text(
            'Crea tu perfil con tu voz',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 6),
          const Text(
            'Ejemplo: "Soy Juan Pérez, plomero con 10 años de experiencia en Coyoacán, mi teléfono es 5512345678"',
            style: TextStyle(color: Colors.black54),
          ),
          const SizedBox(height: 16),
          Center(
            child: GestureDetector(
              onTap: _toggleVoz,
              child: CircleAvatar(
                radius: 40,
                backgroundColor: _escuchando ? Colors.red : Colors.blue,
                child: Icon(_escuchando ? Icons.stop : Icons.mic, size: 40, color: Colors.white),
              ),
            ),
          ),
          Center(
            child: Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Text(_escuchando ? 'Escuchando... toca para detener' : 'Toca el micrófono para hablar'),
            ),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _textoCtrl,
            maxLines: 3,
            decoration: const InputDecoration(
              labelText: 'Tu presentación (editable)',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: _tomarFoto,
            icon: const Icon(Icons.camera_alt),
            label: Text(_foto == null ? 'Tomar foto de rostro o trabajo (Opcional)' : 'Foto lista ✓'),
          ),
          const SizedBox(height: 16),
          FilledButton.icon(
            onPressed: _cargando ? null : _enviarPerfil,
            icon: _cargando
                ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                : const Icon(Icons.auto_awesome),
            label: Text(_cargando ? 'Generando CV con IA...' : 'Publicar mi Perfil'),
          ),
          if (_cvGenerado != null) ...[
            const SizedBox(height: 20),
            Card(
              color: Colors.green.shade50,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('✅ ¡Perfil Publicado!', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.green)),
                    const Divider(),
                    Text('Nombre: ${_cvGenerado!['nombre'] ?? ''}'),
                    Text('Oficio: ${_cvGenerado!['oficio'] ?? ''}'),
                    Text('Zona: ${_cvGenerado!['zona'] ?? ''}'),
                    Text('Teléfono: ${_cvGenerado!['telefono'] ?? ''}'),
                    const SizedBox(height: 8),
                    Text('Resumen CV: ${_cvGenerado!['resumen_profesional'] ?? ''}'),
                  ],
                ),
              ),
            ),
          ]
        ],
      ),
    );
  }
}

// ==================== PESTAÑA 2: VECINO (BUSCAR + WHATSAPP) ====================
class VecinoTab extends StatefulWidget {
  const VecinoTab({super.key});

  @override
  State<VecinoTab> createState() => _VecinoTabState();
}

class _VecinoTabState extends State<VecinoTab> {
  final TextEditingController _busquedaCtrl = TextEditingController();
  bool _buscando = false;
  List<dynamic> _resultados = [];

  Future<void> _buscar() async {
    if (_busquedaCtrl.text.trim().isEmpty) return;
    setState(() => _buscando = true);

    try {
      final res = await http.post(
        Uri.parse('$backendUrl/buscar-vecino'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'consulta': _busquedaCtrl.text}),
      );

      if (res.statusCode == 200) {
        final data = jsonDecode(utf8.decode(res.bodyBytes));
        setState(() {
          _resultados = data['resultados'] ?? data['trabajadores'] ?? [];
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al buscar: $e')),
      );
    } finally {
      setState(() => _buscando = false);
    }
  }

  Future<void> _abrirWhatsApp(String telefono, String oficio) async {
    final limpio = telefono.replaceAll(RegExp(r'[^0-9]'), '');
    final msg = Uri.encodeComponent('Hola, vi tu perfil de $oficio en PuestoYa y me gustaría cotizar un trabajo.');
    final url = Uri.parse('https://wa.me/52$limpio?text=$msg');
    if (await canLaunchUrl(url)) {
      await launchUrl(url, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          TextField(
            controller: _busquedaCtrl,
            decoration: InputDecoration(
              labelText: '¿Qué servicio necesitas y en qué zona?',
              hintText: 'Ej. Plomero urgente en Coyoacán',
              border: const OutlineInputBorder(),
              suffixIcon: IconButton(
                icon: const Icon(Icons.search),
                onPressed: _buscar,
              ),
            ),
            onSubmitted: (_) => _buscar(),
          ),
          const SizedBox(height: 12),
          if (_buscando) const LinearProgressIndicator(),
          Expanded(
            child: _resultados.isEmpty
                ? const Center(child: Text('Escribe lo que necesitas para encontrar trabajadores cerca de ti'))
                : ListView.builder(
                    itemCount: _resultados.length,
                    itemBuilder: (context, index) {
                      final t = _resultados[index];
                      return Card(
                        margin: const EdgeInsets.symmetric(vertical: 6),
                        child: ListTile(
                          leading: const CircleAvatar(child: Icon(Icons.person)),
                          title: Text('${t['nombre'] ?? 'Trabajador'} • ${t['oficio'] ?? ''}'),
                          subtitle: Text('📍 ${t['zona'] ?? ''}\n${t['resumen_profesional'] ?? ''}'),
                          isThreeLine: true,
                          trailing: IconButton(
                            icon: const Icon(Icons.chat, color: Colors.green, size: 30),
                            onPressed: () => _abrirWhatsApp(
                              (t['telefono'] ?? '').toString(),
                              (t['oficio'] ?? 'servicios').toString(),
                            ),
                          ),
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}