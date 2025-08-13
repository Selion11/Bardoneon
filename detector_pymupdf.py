#!/usr/bin/env python3
"""
Detector de líneas de pentagrama en PDFs usando PyMuPDF
No requiere poppler - funciona directamente en Windows
"""

import cv2
import numpy as np
import fitz  # PyMuPDF
import sys
from pathlib import Path

def pdf_a_imagen_pymupdf(ruta_pdf, pagina=0, dpi=200):
    """
    Convierte una página de PDF a imagen usando PyMuPDF
    
    Args:
        ruta_pdf (str): Ruta al archivo PDF
        pagina (int): Número de página (0-indexado)
        dpi (int): Resolución
        
    Returns:
        numpy.ndarray: Imagen en formato OpenCV (BGR)
    """
    try:
        # Abrir el PDF
        doc = fitz.open(ruta_pdf)
        
        if pagina >= len(doc):
            print(f"❌ La página {pagina+1} no existe. El PDF tiene {len(doc)} páginas.")
            return None
        
        # Obtener la página
        page = doc.load_page(pagina)
        
        # Crear matriz de transformación para el DPI deseado
        mat = fitz.Matrix(dpi/72, dpi/72)
        
        # Renderizar página a imagen
        pix = page.get_pixmap(matrix=mat)
        
        # Convertir a array numpy
        img_data = pix.tobytes("ppm")
        
        # Convertir a formato OpenCV
        nparr = np.frombuffer(img_data, np.uint8)
        imagen = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        doc.close()
        return imagen
        
    except Exception as e:
        print(f"❌ Error al convertir PDF: {e}")
        return None

def detectar_lineas_pentagrama(imagen):
    """
    Detecta líneas de pentagrama en una imagen
    
    Args:
        imagen (numpy.ndarray): Imagen en formato OpenCV
        
    Returns:
        tuple: (lineas_detectadas, pentagramas, imagen_resultado)
    """
    
    # Convertir a escala de grises
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    
    # Aplicar filtro gaussiano para reducir ruido
    gris_suave = cv2.GaussianBlur(gris, (3, 3), 0)
    
    # Binarización adaptativa
    binaria = cv2.adaptiveThreshold(
        gris_suave, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
        cv2.THRESH_BINARY_INV, 15, 8
    )
    
    # Crear kernel horizontal para detectar líneas horizontales
    alto_imagen = imagen.shape[0]
    longitud_kernel = min(imagen.shape[1] // 4, 100)  # Ajustar según el tamaño de imagen
    
    kernel_horizontal = cv2.getStructuringElement(cv2.MORPH_RECT, (longitud_kernel, 1))
    
    # Operación morfológica para extraer líneas horizontales
    lineas_horizontales = cv2.morphologyEx(binaria, cv2.MORPH_OPEN, kernel_horizontal)
    
    # Encontrar contornos de las líneas
    contornos, _ = cv2.findContours(lineas_horizontales, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Extraer líneas de los contornos
    lineas = []
    for contorno in contornos:
        x, y, w, h = cv2.boundingRect(contorno)
        
        # Filtrar por longitud mínima
        if w >= longitud_kernel // 2:
            # Guardar como línea (x1, y1, x2, y2)
            y_centro = y + h // 2
            lineas.append((x, y_centro, x + w, y_centro))
    
    return lineas, lineas_horizontales

def agrupar_pentagramas(lineas, tolerancia=30):
    """
    Agrupa líneas en pentagramas
    
    Args:
        lineas (list): Lista de líneas [(x1, y1, x2, y2), ...]
        tolerancia (int): Distancia máxima entre líneas del mismo pentagrama
        
    Returns:
        list: Lista de pentagramas
    """
    if not lineas:
        return []
    
    # Ordenar líneas por posición Y
    lineas_ordenadas = sorted(lineas, key=lambda l: l[1])
    
    pentagramas = []
    grupo_actual = [lineas_ordenadas[0]]
    
    for i in range(1, len(lineas_ordenadas)):
        linea_actual = lineas_ordenadas[i]
        linea_anterior = lineas_ordenadas[i-1]
        
        # Calcular distancia vertical
        distancia = abs(linea_actual[1] - linea_anterior[1])
        
        if distancia <= tolerancia:
            grupo_actual.append(linea_actual)
        else:
            # Si el grupo tiene al menos 3 líneas, considerarlo pentagrama
            if len(grupo_actual) >= 3:
                pentagramas.append(grupo_actual)
            grupo_actual = [linea_actual]
    
    # Agregar el último grupo
    if len(grupo_actual) >= 3:
        pentagramas.append(grupo_actual)
    
    return pentagramas

def analizar_pdf_completo(ruta_pdf):
    """
    Analiza todas las páginas de un PDF
    
    Args:
        ruta_pdf (str): Ruta al archivo PDF
    """
    
    print(f"🔍 Analizando archivo: {ruta_pdf}")
    
    try:
        # Abrir PDF para obtener información
        doc = fitz.open(ruta_pdf)
        num_paginas = len(doc)
        doc.close()
        
        print(f"📚 Páginas encontradas: {num_paginas}")
        
        total_lineas = 0
        total_pentagramas = 0
        archivos_lineas_temporales = []  # Lista para rastrear archivos temporales
        
        for pagina in range(min(num_paginas, 3)):  # Procesar máximo 3 páginas
            print(f"\n📄 Procesando página {pagina + 1}...")
            
            # Convertir página a imagen
            imagen = pdf_a_imagen_pymupdf(ruta_pdf, pagina)
            
            if imagen is None:
                continue
            
            # Detectar líneas
            lineas, imagen_lineas = detectar_lineas_pentagrama(imagen)
            
            # Agrupar en pentagramas
            pentagramas = agrupar_pentagramas(lineas)
            
            print(f"   📏 Líneas detectadas: {len(lineas)}")
            print(f"   🎼 Pentagramas detectados: {len(pentagramas)}")
            
            total_lineas += len(lineas)
            total_pentagramas += len(pentagramas)
            
            # Crear carpeta tmp si no existe
            carpeta_tmp = Path("temporal_files")
            carpeta_tmp.mkdir(exist_ok=True)
            
            # Extraer recortes de cada pentagrama
            nombre_archivo = Path(ruta_pdf).stem
            print(f"     Extrayendo recortes de pentagramas...")
            
            for i, pentagrama in enumerate(pentagramas):
                print(f"     Pentagrama {i+1}: {len(pentagrama)} líneas")
                
                # Calcular límites del pentagrama
                x_min = min(linea[0] for linea in pentagrama)  # X mínimo
                x_max = max(linea[2] for linea in pentagrama)  # X máximo
                y_min = min(linea[1] for linea in pentagrama)  # Y mínimo
                y_max = max(linea[1] for linea in pentagrama)  # Y máximo
                
                # Añadir margen de 20 píxeles (30 hacia abajo)
                margen = 30
                margen_abajo = 30  # 10 píxeles extra hacia abajo
                x_inicio = max(0, x_min - margen)
                y_inicio = max(0, y_min - margen)
                x_fin = min(imagen.shape[1], x_max + margen)
                y_fin = min(imagen.shape[0], y_max + margen_abajo)
                
                # Recortar la imagen
                recorte = imagen[y_inicio:y_fin, x_inicio:x_fin]
                
                # Guardar el recorte en la carpeta tmp
                archivo_recorte = carpeta_tmp / f"{nombre_archivo}_pagina_{pagina+1}_pentagrama_{i+1}.png"
                cv2.imwrite(str(archivo_recorte), recorte)
                
                print(f"       📐 Recorte: X={x_inicio}-{x_fin}, Y={y_inicio}-{y_fin}")
                print(f"       💾 Guardado: {archivo_recorte}")
            
            # También crear imagen completa con líneas marcadas (opcional)
            resultado = imagen.copy()
            colores = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
            
            for i, pentagrama in enumerate(pentagramas):
                color = colores[i % len(colores)]
                for x1, y1, x2, y2 in pentagrama:
                    cv2.line(resultado, (x1, y1), (x2, y2), color, 2)
            
            archivo_completo = f"{nombre_archivo}_pagina_{pagina+1}_completa_marcada.png"
            cv2.imwrite(archivo_completo, resultado)
            archivos_lineas_temporales.append(archivo_completo)  # Este también se borrará
            
            # También guardar la imagen de líneas detectadas
            archivo_lineas = f"{nombre_archivo}_pagina_{pagina+1}_lineas.png"
            cv2.imwrite(archivo_lineas, imagen_lineas)
            archivos_lineas_temporales.append(archivo_lineas)  # Añadir a la lista para borrar después
        
        print(f"\n📊 RESUMEN TOTAL:")
        print(f"   📏 Total de líneas: {total_lineas}")
        print(f"   🎼 Total de pentagramas: {total_pentagramas}")
        
        if total_pentagramas > 0:
            promedio = total_lineas / total_pentagramas
            print(f"   📈 Promedio líneas por pentagrama: {promedio:.1f}")
        
        # Borrar archivos temporales de líneas
        print(f"\n🗑️  Limpiando archivos temporales...")
        for archivo_temp in archivos_lineas_temporales:
            try:
                Path(archivo_temp).unlink()
                print(f"   ✅ Borrado: {archivo_temp}")
            except Exception as e:
                print(f"   ❌ Error al borrar {archivo_temp}: {e}")
        
        print(f"   📁 Se mantuvieron solo los archivos de pentagramas")
        
    except Exception as e:
        print(f"❌ Error al procesar PDF: {e}")

def main():
    """Función principal"""
    
    if len(sys.argv) > 1:
        archivo = sys.argv[1]
        if Path(archivo).exists():
            analizar_pdf_completo(archivo)
        else:
            print(f"❌ Archivo no encontrado: {archivo}")
    else:
        # Buscar archivos PDF en el directorio actual
        archivos_pdf = list(Path(".").glob("*.pdf"))
        
        if archivos_pdf:
            print(f"📁 Archivos PDF encontrados:")
            for i, pdf in enumerate(archivos_pdf, 1):
                print(f"   {i}. {pdf}")
            
            # Procesar el primer PDF
            print(f"\n🎯 Procesando: {archivos_pdf[0]}")
            analizar_pdf_completo(str(archivos_pdf[0]))
        else:
            print("❌ No se encontraron archivos PDF")
            print("💡 Uso: python detector_pymupdf.py <archivo.pdf>")

if __name__ == "__main__":
    main()
