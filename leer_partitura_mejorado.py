# #!/usr/bin/env python3
# """
# Lector de partituras musicales usando music21
# Puede leer archivos MusicXML (.mxl, .xml) y MIDI
# """

# import os
# import sys
# from music21 import converter
# from pathlib import Path

# def leer_partitura(archivo):
#     """
#     Lee una partitura y extrae información de las notas
    
#     Args:
#         archivo (str): Ruta al archivo de partitura
    
#     Returns:
#         bool: True si se procesó correctamente, False en caso contrario
#     """
    
#     # Verificar que el archivo existe
#     if not Path(archivo).exists():
#         print(f"❌ Error: El archivo '{archivo}' no existe")
#         return False
    
#     # Extensiones soportadas
#     extensiones_soportadas = ['.mxl', '.xml', '.musicxml', '.mid', '.midi']
#     extension = Path(archivo).suffix.lower()
    
#     if extension not in extensiones_soportadas:
#         print(f"❌ Error: Extensión '{extension}' no soportada")
#         print(f"Extensiones soportadas: {', '.join(extensiones_soportadas)}")
#         return False
    
#     try:
#         print(f"📄 Cargando archivo: {archivo}")
#         score = converter.parse(archivo)
        
#         # Información general de la partitura
#         print(f"🎵 Título: {score.metadata.title if score.metadata.title else 'Sin título'}")
#         print(f"🎼 Compositor: {score.metadata.composer if score.metadata.composer else 'Desconocido'}")
        
#         # Contar elementos
#         notas = list(score.recurse().notes)
#         compases = len(score.parts[0].getElementsByClass('Measure')) if score.parts else 0
        
#         print(f"📊 Estadísticas:")
#         print(f"   • Total de notas: {len(notas)}")
#         print(f"   • Número de compases: {compases}")
#         print(f"   • Número de partes: {len(score.parts)}")
        
#         print(f"\n🎶 Notas encontradas:")
#         print("-" * 60)
        
#         for i, nota in enumerate(notas[:20]):  # Mostrar solo las primeras 20 notas
#             try:
#                 print(f"{i+1:3d}. Nota: {nota.pitch.name:<3} "
#                       f"Octava: {nota.pitch.octave} "
#                       f"Compás: {nota.measureNumber if nota.measureNumber else 'N/A':<3} "
#                       f"Offset: {float(nota.offset):<6.2f} "
#                       f"Duración: {nota.quarterLength}")
#             except AttributeError as e:
#                 # Manejar acordes u otros objetos que no son notas simples
#                 if hasattr(nota, 'pitches'):  # Es un acorde
#                     notas_acorde = [p.name for p in nota.pitches]
#                     print(f"{i+1:3d}. Acorde: {'/'.join(notas_acorde):<10} "
#                           f"Compás: {nota.measureNumber if nota.measureNumber else 'N/A':<3} "
#                           f"Offset: {float(nota.offset):<6.2f} "
#                           f"Duración: {nota.quarterLength}")
#                 else:
#                     print(f"{i+1:3d}. Elemento musical (no nota simple)")
        
#         if len(notas) > 20:
#             print(f"... y {len(notas) - 20} notas más")
        
#         return True
        
#     except Exception as e:
#         print(f"❌ Error al procesar el archivo: {e}")
#         return False

# def main():
#     """Función principal"""
    
#     # Lista de archivos a intentar (en orden de prioridad)
#     archivos_candidatos = [
#         "Oblivion_A.mxl",
#         "Oblivion_A.xml", 
#         "Oblivion_A.musicxml",
#         "test_simple.mxl",
#         "test_notes.mxl"
#     ]
    
#     # Si se proporciona un archivo como argumento
#     if len(sys.argv) > 1:
#         archivo = sys.argv[1]
#         if leer_partitura(archivo):
#             print("✅ Procesamiento completado exitosamente")
#         else:
#             print("❌ Falló el procesamiento")
#         return
    
#     # Buscar archivos automáticamente
#     print("🔍 Buscando archivos de partitura...")
    
#     archivo_encontrado = None
#     for archivo in archivos_candidatos:
#         if Path(archivo).exists():
#             print(f"✅ Encontrado: {archivo}")
#             archivo_encontrado = archivo
#             break
#         else:
#             print(f"⏭️  No encontrado: {archivo}")
    
#     if archivo_encontrado:
#         print(f"\n🎯 Procesando: {archivo_encontrado}")
#         if leer_partitura(archivo_encontrado):
#             print("\n✅ Procesamiento completado exitosamente")
#         else:
#             print("\n❌ Falló el procesamiento")
#     else:
#         print("\n❌ No se encontraron archivos de partitura válidos")
#         print("💡 Usa: python3 leer_partitura_mejorado.py <archivo>")
#         print("   Donde <archivo> puede ser .mxl, .xml, .musicxml, .mid, .midi")

# if __name__ == "__main__":
#     main()
