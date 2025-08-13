from music21 import converter
import sys

try:
    # Cargar el archivo generado por Audiveris
    score = converter.parse("Oblivion_A.mxl")
    
    # Procesamiento silencioso de las notas
    for n in score.recurse().notes:
        if hasattr(n, 'pitch'):  # Nota simple
            pass
        elif hasattr(n, 'pitches'):  # Acorde
            pass
            
except FileNotFoundError:
    print("Error: No se encontró el archivo Oblivion_A.mxl", file=sys.stderr)
except Exception as e:
    print(f"Error al procesar la partitura: {e}", file=sys.stderr)