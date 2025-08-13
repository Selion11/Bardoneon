# #!/usr/bin/env python3
# """
# Analizador de claves musicales en archivos MusicXML
# Muestra qué claves (treble, bass, etc.) están presentes en cada pentagrama
# """

# from music21 import converter
# import sys

# # Mapeo de nombres anglosajones a latinos
# nombres_latino = {
#     'C': 'Do',
#     'D': 'Re', 
#     'E': 'Mi',
#     'F': 'Fa',
#     'G': 'Sol',
#     'A': 'La',
#     'B': 'Si'
# }

# def convertir_nota_a_latino(nombre_nota):
#     """Convierte un nombre de nota del formato anglo al latino"""
#     if not nombre_nota or len(nombre_nota) == 0:
#         return nombre_nota
    
#     # Extraer la nota base (primera letra)
#     nota_base = nombre_nota[0].upper()
    
#     # Obtener la parte de alteraciones (# o b)
#     alteraciones = nombre_nota[1:] if len(nombre_nota) > 1 else ''
    
#     # Convertir la nota base a latino
#     if nota_base in nombres_latino:
#         return nombres_latino[nota_base] + alteraciones
#     else:
#         return nombre_nota

# def analizar_claves(archivo_mxl):
#     """Analiza las claves presentes en un archivo MusicXML"""
    
#     try:
#         print(f"🎼 Analizando claves en: {archivo_mxl}")
#         print("=" * 60)
        
#         # Cargar el archivo
#         score = converter.parse(archivo_mxl)
        
#         # Información general
#         print(f"📊 Número de partes: {len(score.parts)}")
#         print()
        
#         # Analizar cada parte
#         for i, part in enumerate(score.parts):
#             print(f"📝 PARTE {i+1}:")
#             print("-" * 30)
            
#             # Buscar claves en esta parte
#             claves = list(part.recurse().getElementsByClass('Clef'))
#             measures = list(part.getElementsByClass('Measure'))
            
#             print(f"   • Compases: {len(measures)}")
#             print(f"   • Claves encontradas: {len(claves)}")
            
#             if claves:
#                 for j, clave in enumerate(claves):
#                     print(f"     {j+1}. {clave.sign} (línea {clave.line}) - Octava: {clave.octaveChange if hasattr(clave, 'octaveChange') else 0}")
#                     print(f"        Nombre completo: {clave.name}")
#             else:
#                 print("     ⚠️  No se detectaron claves específicas")
            
#             # Mostrar algunas notas de ejemplo para verificar el rango
#             notas_parte = list(part.recurse().notes)
#             if notas_parte:
#                 print(f"   • Total de notas en esta parte: {len(notas_parte)}")
                
#                 # Mostrar rango de octavas
#                 octavas = []
#                 for nota in notas_parte:
#                     if hasattr(nota, 'pitch'):
#                         octavas.append(nota.pitch.octave)
#                     elif hasattr(nota, 'pitches'):
#                         octavas.extend([p.octave for p in nota.pitches])
                
#                 if octavas:
#                     print(f"   • Rango de octavas: {min(octavas)} - {max(octavas)}")
                
#                 # Mostrar primeras 5 notas
#                 print(f"   • Primeras 5 notas:")
#                 for k, nota in enumerate(notas_parte[:5]):
#                     if hasattr(nota, 'pitch'):
#                         nota_latino = convertir_nota_a_latino(nota.pitch.name)
#                         print(f"     {k+1}. {nota_latino}{nota.pitch.octave}")
#                     elif hasattr(nota, 'pitches'):
#                         notas_str = [f"{convertir_nota_a_latino(p.name)}{p.octave}" for p in nota.pitches]
#                         print(f"     {k+1}. Acorde: {'/'.join(notas_str)}")
            
#             print()
        
#         print("=" * 60)
#         print("ℹ️  Información sobre claves:")
#         print("   • Clave de Sol: treble (línea 2)")
#         print("   • Clave de Fa: bass (línea 4)")
#         print("   • Clave de Do: alto/tenor (línea 3 o 4)")
        
#     except Exception as e:
#         print(f"❌ Error: {e}")

# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("Uso: python3 analizar_claves.py <archivo.mxl>")
#         sys.exit(1)
    
#     analizar_claves(sys.argv[1])
