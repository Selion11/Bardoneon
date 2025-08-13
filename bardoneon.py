#!/usr/bin/env python3
"""
Conversor y Lector de Partituras Musicales
Integra Audiveris (PDF → MusicXML) y music21 (análisis musical)
"""

import os
import sys
import subprocess
from pathlib import Path
from music21 import converter

class ConversorPartitura:
    def __init__(self):
        self.audiveris_path = "/opt/audiveris/bin/Audiveris"
        # Mapeo de nombres anglosajones a latinos
        self.nombres_latino = {
            'C': 'Do',
            'D': 'Re', 
            'E': 'Mi',
            'F': 'Fa',
            'G': 'Sol',
            'A': 'La',
            'B': 'Si'
        }
        
    def verificar_audiveris(self):
        """Verifica que Audiveris esté instalado y disponible"""
        if not Path(self.audiveris_path).exists():
            print("ERROR: Audiveris no encontrado en /opt/audiveris/bin/Audiveris")
            return False
        return True
    
    def convertir_nota_a_latino(self, nombre_nota):
        """
        Convierte un nombre de nota del formato anglo (C, D, E...) al latino (Do, Re, Mi...)
        
        Args:
            nombre_nota (str): Nombre de la nota en formato anglo (ej: 'C#', 'Bb', 'F')
        
        Returns:
            str: Nombre de la nota en formato latino (ej: 'Do#', 'Sib', 'Fa')
        """
        if not nombre_nota or len(nombre_nota) == 0:
            return nombre_nota
        
        # Extraer la nota base (primera letra)
        nota_base = nombre_nota[0].upper()
        
        # Obtener la parte de alteraciones (# o b)
        alteraciones = nombre_nota[1:] if len(nombre_nota) > 1 else ''
        
        # Convertir la nota base a latino
        if nota_base in self.nombres_latino:
            return self.nombres_latino[nota_base] + alteraciones
        else:
            return nombre_nota  # Si no se puede convertir, devolver original
    
    def convertir_pdf_a_mxl(self, pdf_path, output_path=None):
        """
        Convierte PDF a MusicXML usando Audiveris
        
        Args:
            pdf_path (str): Ruta al archivo PDF
            output_path (str): Ruta de salida opcional (si no se especifica, usa el mismo nombre)
        
        Returns:
            str|None: Ruta al archivo MXL generado o None si falla
        """
        
        # Verificar que el archivo PDF existe
        if not Path(pdf_path).exists():
            print(f"ERROR: El archivo PDF '{pdf_path}' no existe")
            return None
        
        # Verificar que Audiveris está disponible
        if not self.verificar_audiveris():
            return None
        
        # Determinar el archivo de salida
        if not output_path:
            output_path = str(Path(pdf_path).with_suffix('.mxl'))
        
        try:
            # Ejecutar Audiveris en modo batch
            cmd = [self.audiveris_path, '-batch', '-export', pdf_path]
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=Path(pdf_path).parent  # Ejecutar en el directorio del PDF
            )
            
            # Verificar que se generó el archivo
            if Path(output_path).exists():
                return output_path
            else:
                print("ERROR: No se generó el archivo MXL")
                if result.stderr:
                    print(f"ERROR: {result.stderr}")
                return None
                
        except subprocess.SubprocessError as e:
            print(f"ERROR: {e}")
            return None
        except Exception as e:
            print(f"ERROR: {e}")
            return None
    
    def exportar_notas_txt(self, notas, archivo_txt, titulo="Sin título", compositor="Desconocido"):
        """
        Exporta todas las notas a un archivo de texto
        
        Args:
            notas (list): Lista de notas extraídas de music21
            archivo_txt (str): Ruta del archivo TXT de salida
            titulo (str): Título de la partitura
            compositor (str): Compositor de la partitura
        """
        
        try:
            with open(archivo_txt, 'w', encoding='utf-8') as f:
                # Encabezado del archivo
                f.write("=" * 80 + "\n")
                f.write("ANÁLISIS MUSICAL - NOTAS EXTRAÍDAS\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Título: {titulo}\n")
                f.write(f"Compositor: {compositor}\n")
                f.write(f"Total de notas: {len(notas)}\n")
                f.write(f"Fecha de análisis: {self.obtener_fecha_actual()}\n\n")
                
                f.write("-" * 80 + "\n")
                f.write("LISTADO COMPLETO DE NOTAS\n")
                f.write("-" * 80 + "\n\n")
                
                # Encabezado de la tabla (sin columnas de offset y duración)
                f.write(f"{'Nº':<4} {'Tipo':<8} {'Nota/Acorde':<20} {'Octava':<7} {'Compás':<7}\n")
                f.write("-" * 50 + "\n")
                
                # Exportar todas las notas (sin offset y duración)
                for i, nota in enumerate(notas):
                    try:
                        if hasattr(nota, 'pitch'):  # Nota simple
                            nota_latino = self.convertir_nota_a_latino(nota.pitch.name)
                            f.write(f"{i+1:<4} {'Nota':<8} {nota_latino:<20} "
                                   f"{nota.pitch.octave:<7} "
                                   f"{nota.measureNumber if nota.measureNumber else 'N/A':<7}\n")
                        elif hasattr(nota, 'pitches'):  # Acorde
                            notas_acorde = [self.convertir_nota_a_latino(p.name) for p in nota.pitches]
                            acorde_str = '/'.join(notas_acorde)
                            f.write(f"{i+1:<4} {'Acorde':<8} {acorde_str:<20} "
                                   f"{'Multi':<7} "
                                   f"{nota.measureNumber if nota.measureNumber else 'N/A':<7}\n")
                        else:
                            f.write(f"{i+1:<4} {'Otro':<8} {type(nota).__name__:<20} "
                                   f"{'N/A':<7} "
                                   f"{nota.measureNumber if nota.measureNumber else 'N/A':<7}\n")
                    except Exception as e:
                        f.write(f"{i+1:<4} {'Error':<8} {'Error al procesar':<20} "
                               f"{'N/A':<7} {'N/A':<7}\n")
                
                # Fin del archivo (se removió el resumen estadístico)
                f.write("\n" + "=" * 50 + "\n")
                f.write("Fin del análisis\n")
                f.write("=" * 50 + "\n")
            
            print(f"📄 Notas exportadas a: {archivo_txt}")
            return True
            
        except Exception as e:
            print(f"ERROR: {e}")
            return False
    
    def obtener_fecha_actual(self):
        """Obtiene la fecha y hora actual en formato legible"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def limpiar_archivos_temporales(self, archivo_base, mantener_txt=True, incluir_mxl=True):
        """
        Elimina archivos temporales generados por Audiveris
        
        Args:
            archivo_base (str): Ruta base del archivo (sin extensión)
            mantener_txt (bool): Si True, mantiene el archivo .txt
            incluir_mxl (bool): Si True, también elimina archivos .mxl
        """
        
        # Siempre eliminar archivos temporales (.omr y .log)
        extensiones_temporales = ['.omr']
        if incluir_mxl:
            extensiones_temporales.append('.mxl')
            
        archivos_eliminados = []
        
        try:
            # Obtener el directorio y nombre base del archivo
            path_base = Path(archivo_base)
            directorio = path_base.parent
            nombre_base = path_base.stem
            
            # Buscar y eliminar archivos específicos del proyecto
            for extension in extensiones_temporales:
                archivo_temp = directorio / f"{nombre_base}{extension}"
                if archivo_temp.exists():
                    try:
                        archivo_temp.unlink()
                        archivos_eliminados.append(str(archivo_temp))
                    except Exception as e:
                        print(f"ERROR eliminando {archivo_temp.name}: {e}")
            
            # Buscar y eliminar TODOS los archivos .log en el directorio actual
            log_files = list(directorio.glob("*.log"))
            for log_file in log_files:
                try:
                    log_file.unlink()
                    archivos_eliminados.append(str(log_file))
                except Exception as e:
                    print(f"ERROR eliminando {log_file.name}: {e}")
                
        except Exception as e:
            print(f"ERROR durante la limpieza: {e}")
        
        return archivos_eliminados
    
    def leer_partitura(self, archivo_mxl, exportar_txt=True):
        """
        Lee una partitura MusicXML y extrae información musical
        
        Args:
            archivo_mxl (str): Ruta al archivo MusicXML
            exportar_txt (bool): Si True, exporta las notas a un archivo .txt
        
        Returns:
            bool: True si se procesó correctamente, False en caso contrario
        """
        
        # Verificar que el archivo existe
        if not Path(archivo_mxl).exists():
            print(f"❌ Error: El archivo '{archivo_mxl}' no existe")
            return False
        
        # Extensiones soportadas
        extensiones_soportadas = ['.mxl', '.xml', '.musicxml', '.mid', '.midi']
        extension = Path(archivo_mxl).suffix.lower()
        
        if extension not in extensiones_soportadas:
            print(f"❌ Error: Extensión '{extension}' no soportada")
            print(f"Extensiones soportadas: {', '.join(extensiones_soportadas)}")
            return False
        
        try:
            print(f"\n🎼 Analizando partitura con music21...")
            print(f"📄 Cargando archivo: {archivo_mxl}")
            score = converter.parse(archivo_mxl)
            
            # Información general de la partitura
            titulo = score.metadata.title if score.metadata and score.metadata.title else 'Sin título'
            compositor = score.metadata.composer if score.metadata and score.metadata.composer else 'Desconocido'
            
            print(f"🎵 Título: {titulo}")
            print(f"🎼 Compositor: {compositor}")
            
            # Contar elementos
            notas = list(score.recurse().notes)
            compases = len(score.parts[0].getElementsByClass('Measure')) if score.parts else 0
            
            print(f"\n📊 Estadísticas:")
            print(f"   • Total de notas: {len(notas)}")
            print(f"   • Número de compases: {compases}")
            print(f"   • Número de partes: {len(score.parts)}")
            
            print(f"\n🎶 Primeras 20 notas:")
            print("-" * 70)
            
            for i, nota in enumerate(notas[:20]):
                try:
                    if hasattr(nota, 'pitch'):  # Nota simple
                        nota_latino = self.convertir_nota_a_latino(nota.pitch.name)
                        print(f"{i+1:3d}. Nota: {nota_latino:<3} "
                              f"Octava: {nota.pitch.octave} "
                              f"Compás: {nota.measureNumber if nota.measureNumber else 'N/A':<3} "
                              f"Offset: {float(nota.offset):<6.2f} "
                              f"Duración: {nota.quarterLength}")
                    elif hasattr(nota, 'pitches'):  # Acorde
                        notas_acorde = [self.convertir_nota_a_latino(p.name) for p in nota.pitches]
                        print(f"{i+1:3d}. Acorde: {'/'.join(notas_acorde):<12} "
                              f"Compás: {nota.measureNumber if nota.measureNumber else 'N/A':<3} "
                              f"Offset: {float(nota.offset):<6.2f} "
                              f"Duración: {nota.quarterLength}")
                    else:
                        print(f"{i+1:3d}. Elemento musical (tipo: {type(nota).__name__})")
                        
                except AttributeError as e:
                    print(f"{i+1:3d}. Error procesando nota: {e}")
            
            if len(notas) > 20:
                print(f"... y {len(notas) - 20} notas más")

            # Exportar a archivo TXT si se solicita
            if exportar_txt:
                archivo_txt = str(Path(archivo_mxl).with_suffix('.txt'))
                self.exportar_notas_txt(notas, archivo_txt, titulo, compositor)
            
            return True
            
        except Exception as e:
            print(f"❌ Error al procesar el archivo: {e}")
            return False
    
    def procesar_archivo_completo(self, archivo_pdf, exportar_txt=True, limpiar_temporales=True):
        """
        Proceso completo: PDF → MXL → Análisis → Limpieza
        
        Args:
            archivo_pdf (str): Ruta al archivo PDF
            exportar_txt (bool): Si True, exporta las notas a TXT
            limpiar_temporales (bool): Si True, elimina archivos temporales al final
        
        Returns:
            bool: True si todo el proceso fue exitoso
        """
        print(f"🚀 Iniciando proceso completo para: {archivo_pdf}")
        print("=" * 60)
        
        archivo_base = str(Path(archivo_pdf).with_suffix(''))
        
        try:
            # Paso 1: Convertir PDF a MXL
            archivo_mxl = self.convertir_pdf_a_mxl(archivo_pdf)
            if not archivo_mxl:
                print("❌ Falló la conversión PDF → MXL")
                # Limpiar archivos temporales aunque falle la conversión
                if limpiar_temporales:
                    self.limpiar_archivos_temporales(archivo_base, mantener_txt=False, incluir_mxl=False)
                return False
            
            # Paso 2: Analizar la partitura
            if self.leer_partitura(archivo_mxl, exportar_txt):
                print("\n✅ Proceso completo exitoso!")
                if exportar_txt:
                    archivo_txt = str(Path(archivo_pdf).with_suffix('.txt'))
                    print(f"📁 Archivos generados:")
                    print(f"   • Notas TXT: {archivo_txt}")
                
                # Paso 3: Limpiar archivos temporales (incluir .mxl si corresponde)
                if limpiar_temporales:
                    self.limpiar_archivos_temporales(archivo_base, mantener_txt=exportar_txt, incluir_mxl=True)
                
                print("=" * 60)
                return True
            else:
                print("\n❌ Falló el análisis musical")
                # Limpiar archivos temporales aunque falle el análisis
                if limpiar_temporales:
                    self.limpiar_archivos_temporales(archivo_base, mantener_txt=False, incluir_mxl=True)
                return False
                
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            # Siempre limpiar archivos temporales en caso de error
            if limpiar_temporales:
                self.limpiar_archivos_temporales(archivo_base, mantener_txt=False, incluir_mxl=True)
            return False

def main():
    """Función principal"""
    
    conversor = ConversorPartitura()
    
    if len(sys.argv) < 2:
        print("🎼 Conversor y Lector de Partituras Musicales")
        print("=" * 50)
        print("Uso:")
        print(f"  {sys.argv[0]} <archivo.pdf>         # Proceso completo (PDF → TXT) + limpieza")
        print(f"  {sys.argv[0]} --mxl <archivo.mxl>    # Solo análisis (MXL → TXT)")
        print(f"  {sys.argv[0]} --no-txt <archivo.pdf>  # Sin exportar TXT")
        print(f"  {sys.argv[0]} --no-clean <archivo.pdf> # Sin limpiar archivos temporales")
        print()
        
        # Buscar archivos PDF automáticamente
        pdfs_encontrados = list(Path('.').glob('*.pdf'))
        if pdfs_encontrados:
            print("📁 PDFs encontrados en el directorio actual:")
            for pdf in pdfs_encontrados:
                print(f"   • {pdf}")
            print(f"\n💡 Usa: python3 {sys.argv[0]} {pdfs_encontrados[0]}")
        else:
            print("❌ No se encontraron archivos PDF en el directorio actual")
        
        return 1
    
    # Verificar opciones especiales
    exportar_txt = True
    limpiar_temporales = True
    archivo_a_procesar = None
    
    if len(sys.argv) >= 2:
        if sys.argv[1] == '--no-txt' and len(sys.argv) > 2:
            exportar_txt = False
            archivo_a_procesar = sys.argv[2]
        elif sys.argv[1] == '--no-clean' and len(sys.argv) > 2:
            limpiar_temporales = False
            archivo_a_procesar = sys.argv[2]
        elif sys.argv[1] == '--mxl' and len(sys.argv) > 2:
            archivo_mxl = sys.argv[2]
            if conversor.leer_partitura(archivo_mxl, exportar_txt):
                print("✅ Análisis completado exitosamente")
                return 0
            else:
                print("❌ Falló el análisis")
                return 1
        else:
            archivo_a_procesar = sys.argv[1]
    
    if not archivo_a_procesar:
        print("❌ Error: No se especificó archivo a procesar")
        return 1
    
    # Verificar que es un archivo PDF
    if not archivo_a_procesar.lower().endswith('.pdf'):
        print("❌ Error: El archivo debe ser un PDF")
        return 1
    
    # Ejecutar proceso completo con opciones de exportar TXT y limpiar temporales
    if conversor.procesar_archivo_completo(archivo_a_procesar, exportar_txt, limpiar_temporales):
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
