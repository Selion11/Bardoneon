# #!/usr/bin/env python3
# """
# Conversor automático de PDF a MusicXML usando Audiveris y lector con music21
# Integra tu programa test.py para detección de imágenes con Audiveris para OCR musical
# """

# import os
# import sys
# import subprocess
# import tempfile
# from pathlib import Path
# from music21 import converter

# def convertir_pdf_con_audiveris_local(pdf_path, output_dir=None):
#     """
#     Convierte PDF a MusicXML usando tu instalación local de Audiveris
#     """
#     audiveris_path = "/root/win_dek/Resources/audiveris"
    
#     if not output_dir:
#         output_dir = Path(pdf_path).parent
    
#     try:
#         # Cambiar al directorio de Audiveris
#         original_dir = os.getcwd()
#         os.chdir(audiveris_path)
        
#         # Intentar usar el JAR de Audiveris
#         jar_path = "app/build/jar/audiveris.jar"
        
#         if Path(jar_path).exists():
#             print(f"🔧 Usando Audiveris local: {audiveris_path}")
            
#             # Comando para ejecutar Audiveris en modo batch
#             cmd = [
#                 "java", "-jar", jar_path,
#                 "-batch", "-export",
#                 str(Path(original_dir) / pdf_path)
#             ]
            
#             print(f"📝 Ejecutando: {' '.join(cmd)}")
#             result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
#             if result.returncode == 0:
#                 # Buscar el archivo MusicXML generado
#                 pdf_name = Path(pdf_path).stem
#                 possible_files = [
#                     f"{pdf_name}.mxl",
#                     f"{pdf_name}.xml",
#                     f"{pdf_name}.musicxml"
#                 ]
                
#                 for filename in possible_files:
#                     if Path(filename).exists():
#                         # Mover el archivo al directorio de destino
#                         output_path = Path(output_dir) / filename
#                         os.rename(filename, output_path)
#                         print(f"✅ Archivo generado: {output_path}")
#                         os.chdir(original_dir)
#                         return str(output_path)
                
#                 print("⚠️  Audiveris se ejecutó pero no se encontró archivo de salida")
#                 print(f"Salida: {result.stdout}")
#                 print(f"Errores: {result.stderr}")
#             else:
#                 print(f"❌ Error en Audiveris: {result.stderr}")
                
#         else:
#             print(f"❌ No se encontró el JAR de Audiveris en: {jar_path}")
            
#         os.chdir(original_dir)
#         return None
        
#     except subprocess.TimeoutExpired:
#         print("⏱️  Tiempo de espera agotado para Audiveris")
#         os.chdir(original_dir)
#         return None
#     except Exception as e:
#         print(f"❌ Error ejecutando Audiveris: {e}")
#         os.chdir(original_dir)
#         return None

# def leer_partitura_completo(archivo_mxl):
#     """
#     Lee una partitura MusicXML y muestra información detallada
#     """
#     try:
#         print(f"📄 Cargando archivo MusicXML: {archivo_mxl}")
#         score = converter.parse(archivo_mxl)
        
#         # Información general
#         print(f"\n🎵 === INFORMACIÓN DE LA PARTITURA ===")
#         print(f"Título: {score.metadata.title if score.metadata.title else 'Sin título'}")
#         print(f"Compositor: {score.metadata.composer if score.metadata.composer else 'Desconocido'}")
        
#         # Estadísticas
#         notas = list(score.recurse().notes)
#         acordes = [n for n in notas if hasattr(n, 'pitches') and len(n.pitches) > 1]
#         notas_simples = [n for n in notas if hasattr(n, 'pitch')]
        
#         print(f"\n📊 === ESTADÍSTICAS ===")
#         print(f"Total de elementos musicales: {len(notas)}")
#         print(f"Notas simples: {len(notas_simples)}")
#         print(f"Acordes: {len(acordes)}")
#         print(f"Número de partes: {len(score.parts)}")
        
#         if score.parts:
#             compases = len(score.parts[0].getElementsByClass('Measure'))
#             print(f"Número de compases: {compases}")
        
#         # Análisis por partes
#         for i, part in enumerate(score.parts):
#             print(f"\n🎼 === PARTE {i+1} ===")
#             part_notes = list(part.recurse().notes)
#             print(f"Notas en esta parte: {len(part_notes)}")
            
#             if hasattr(part, 'partName') and part.partName:
#                 print(f"Nombre: {part.partName}")
        
#         # Mostrar las primeras notas
#         print(f"\n🎶 === PRIMERAS 15 NOTAS ===")
#         print("-" * 70)
        
#         for i, nota in enumerate(notas[:15]):
#             try:
#                 if hasattr(nota, 'pitch'):  # Nota simple
#                     print(f"{i+1:2d}. Nota: {nota.pitch.name:<3} "
#                           f"Octava: {nota.pitch.octave} "
#                           f"Compás: {nota.measureNumber if nota.measureNumber else 'N/A':<3} "
#                           f"Offset: {float(nota.offset):<6.2f} "
#                           f"Duración: {nota.quarterLength}")
                          
#                 elif hasattr(nota, 'pitches'):  # Acorde
#                     notas_acorde = [p.name for p in nota.pitches]
#                     print(f"{i+1:2d}. Acorde: {'/'.join(notas_acorde):<12} "
#                           f"Compás: {nota.measureNumber if nota.measureNumber else 'N/A':<3} "
#                           f"Offset: {float(nota.offset):<6.2f} "
#                           f"Duración: {nota.quarterLength}")
#                 else:
#                     print(f"{i+1:2d}. Elemento musical (tipo: {type(nota).__name__})")
                    
#             except Exception as e:
#                 print(f"{i+1:2d}. Error procesando elemento: {e}")
        
#         if len(notas) > 15:
#             print(f"\n... y {len(notas) - 15} elementos más")
        
#         return True
        
#     except Exception as e:
#         print(f"❌ Error procesando archivo MusicXML: {e}")
#         return False

# def main():
#     """Función principal del conversor"""
    
#     if len(sys.argv) < 2:
#         print("💡 Uso: python3 conversor_completo.py <archivo.pdf>")
#         print("   Ejemplo: python3 conversor_completo.py Oblivion_A.pdf")
#         return
    
#     pdf_file = sys.argv[1]
    
#     if not Path(pdf_file).exists():
#         print(f"❌ Error: No se encontró el archivo '{pdf_file}'")
#         return
    
#     if not pdf_file.lower().endswith('.pdf'):
#         print(f"❌ Error: El archivo debe ser un PDF")
#         return
    
#     print(f"🚀 === CONVERSOR PDF → MusicXML → ANÁLISIS ===")
#     print(f"📄 Archivo de entrada: {pdf_file}")
    
#     # Paso 1: Convertir PDF a MusicXML
#     print(f"\n🔄 Paso 1: Convirtiendo PDF a MusicXML...")
#     mxl_file = convertir_pdf_con_audiveris_local(pdf_file)
    
#     if mxl_file and Path(mxl_file).exists():
#         print(f"✅ Conversión exitosa: {mxl_file}")
        
#         # Paso 2: Analizar con music21
#         print(f"\n🔄 Paso 2: Analizando partitura con music21...")
#         if leer_partitura_completo(mxl_file):
#             print(f"\n✅ === PROCESO COMPLETADO EXITOSAMENTE ===")
#             print(f"📁 Archivos generados:")
#             print(f"   • PDF original: {pdf_file}")
#             print(f"   • MusicXML: {mxl_file}")
#         else:
#             print(f"\n❌ Error en el análisis musical")
#     else:
#         print(f"\n❌ No se pudo convertir el PDF a MusicXML")
#         print(f"💡 Sugerencias:")
#         print(f"   • Verifica que Audiveris esté compilado correctamente")
#         print(f"   • Asegúrate que el PDF contenga música reconocible")
#         print(f"   • Intenta con un PDF de mejor calidad")

# if __name__ == "__main__":
#     main()
