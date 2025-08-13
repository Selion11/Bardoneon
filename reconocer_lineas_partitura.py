# #!/usr/bin/env python3
# """
# Reconocedor de líneas de partituras en archivos PDF
# Utiliza OpenCV y pdf2image para detectar y analizar las líneas del pentagrama
# """

# import cv2
# import numpy as np
# import matplotlib.pyplot as plt
# from pdf2image import convert_from_path
# from PIL import Image
# import os
# import sys
# from pathlib import Path

# class ReconocedorLineasPartitura:
#     def __init__(self):
#         self.imagenes_procesadas = []
#         self.lineas_detectadas = []
        
#     def pdf_a_imagenes(self, ruta_pdf, dpi=300):
#         """
#         Convierte un PDF a imágenes
        
#         Args:
#             ruta_pdf (str): Ruta al archivo PDF
#             dpi (int): Resolución para la conversión
            
#         Returns:
#             list: Lista de imágenes PIL
#         """
#         try:
#             print(f"📄 Convirtiendo PDF a imágenes (DPI: {dpi})...")
#             imagenes = convert_from_path(ruta_pdf, dpi=dpi)
#             print(f"✅ Convertidas {len(imagenes)} páginas")
#             return imagenes
#         except Exception as e:
#             print(f"❌ Error al convertir PDF: {e}")
#             return []
    
#     def preprocesar_imagen(self, imagen_pil):
#         """
#         Preprocesa una imagen para la detección de líneas
        
#         Args:
#             imagen_pil (PIL.Image): Imagen en formato PIL
            
#         Returns:
#             numpy.ndarray: Imagen procesada en escala de grises
#         """
#         # Convertir PIL a OpenCV
#         imagen_cv = cv2.cvtColor(np.array(imagen_pil), cv2.COLOR_RGB2BGR)
        
#         # Convertir a escala de grises
#         gris = cv2.cvtColor(imagen_cv, cv2.COLOR_BGR2GRAY)
        
#         # Aplicar filtro gaussiano para reducir ruido
#         gris_suavizado = cv2.GaussianBlur(gris, (3, 3), 0)
        
#         # Binarización adaptativa
#         binaria = cv2.adaptiveThreshold(
#             gris_suavizado, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
#             cv2.THRESH_BINARY_INV, 15, 10
#         )
        
#         return gris, binaria
    
#     def detectar_lineas_horizontales(self, imagen_binaria, min_longitud=100):
#         """
#         Detecta líneas horizontales en la imagen (líneas del pentagrama)
        
#         Args:
#             imagen_binaria (numpy.ndarray): Imagen binarizada
#             min_longitud (int): Longitud mínima de línea a detectar
            
#         Returns:
#             list: Lista de líneas detectadas [(x1, y1, x2, y2), ...]
#         """
#         # Crear kernel horizontal para detectar líneas horizontales
#         kernel_horizontal = cv2.getStructuringElement(cv2.MORPH_RECT, (min_longitud, 1))
        
#         # Detectar líneas horizontales
#         lineas_horizontales = cv2.morphologyEx(imagen_binaria, cv2.MORPH_OPEN, kernel_horizontal)
        
#         # Encontrar contornos
#         contornos, _ = cv2.findContours(lineas_horizontales, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
#         lineas = []
#         for contorno in contornos:
#             # Obtener el rectángulo que encierra el contorno
#             x, y, w, h = cv2.boundingRect(contorno)
            
#             # Filtrar por longitud mínima
#             if w >= min_longitud:
#                 # Guardar como línea (x1, y1, x2, y2)
#                 lineas.append((x, y + h//2, x + w, y + h//2))
        
#         return lineas, lineas_horizontales
    
#     def agrupar_pentagramas(self, lineas, tolerancia_y=20):
#         """
#         Agrupa las líneas en pentagramas (conjuntos de 5 líneas)
        
#         Args:
#             lineas (list): Lista de líneas detectadas
#             tolerancia_y (int): Tolerancia en píxeles para agrupar líneas
            
#         Returns:
#             list: Lista de pentagramas, cada uno con 5 líneas
#         """
#         # Ordenar líneas por posición Y
#         lineas_ordenadas = sorted(lineas, key=lambda l: l[1])
        
#         pentagramas = []
#         grupo_actual = []
        
#         for linea in lineas_ordenadas:
#             if not grupo_actual:
#                 grupo_actual.append(linea)
#             else:
#                 # Calcular distancia vertical a la línea anterior
#                 distancia = abs(linea[1] - grupo_actual[-1][1])
                
#                 if distancia <= tolerancia_y * 2:  # Líneas del mismo pentagrama
#                     grupo_actual.append(linea)
#                 else:  # Nueva línea está demasiado lejos, nuevo pentagrama
#                     if len(grupo_actual) >= 4:  # Al menos 4 líneas para considerar pentagrama
#                         pentagramas.append(grupo_actual)
#                     grupo_actual = [linea]
        
#         # Agregar el último grupo si tiene suficientes líneas
#         if len(grupo_actual) >= 4:
#             pentagramas.append(grupo_actual)
        
#         return pentagramas
    
#     def visualizar_resultados(self, imagen_original, lineas, pentagramas, titulo="Líneas detectadas"):
#         """
#         Visualiza los resultados de la detección
        
#         Args:
#             imagen_original (numpy.ndarray): Imagen original
#             lineas (list): Lista de todas las líneas detectadas
#             pentagramas (list): Lista de pentagramas agrupados
#             titulo (str): Título para el gráfico
#         """
#         plt.figure(figsize=(15, 10))
        
#         # Mostrar imagen original
#         plt.subplot(2, 1, 1)
#         plt.imshow(imagen_original, cmap='gray')
#         plt.title(f"{titulo} - Original")
#         plt.axis('off')
        
#         # Mostrar imagen con líneas detectadas
#         plt.subplot(2, 1, 2)
#         imagen_con_lineas = imagen_original.copy()
#         if len(imagen_con_lineas.shape) == 2:
#             imagen_con_lineas = cv2.cvtColor(imagen_con_lineas, cv2.COLOR_GRAY2RGB)
        
#         # Dibujar todas las líneas en azul
#         for x1, y1, x2, y2 in lineas:
#             cv2.line(imagen_con_lineas, (x1, y1), (x2, y2), (0, 0, 255), 2)
        
#         # Dibujar pentagramas en diferentes colores
#         colores_pentagrama = [(255, 0, 0), (0, 255, 0), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
        
#         for i, pentagrama in enumerate(pentagramas):
#             color = colores_pentagrama[i % len(colores_pentagrama)]
#             for x1, y1, x2, y2 in pentagrama:
#                 cv2.line(imagen_con_lineas, (x1, y1), (x2, y2), color, 3)
        
#         plt.imshow(imagen_con_lineas)
#         plt.title(f"{titulo} - {len(lineas)} líneas, {len(pentagramas)} pentagramas")
#         plt.axis('off')
        
#         plt.tight_layout()
#         plt.show()
    
#     def procesar_pdf(self, ruta_pdf, mostrar_resultados=True, guardar_imagenes=False):
#         """
#         Procesa un archivo PDF completo
        
#         Args:
#             ruta_pdf (str): Ruta al archivo PDF
#             mostrar_resultados (bool): Si mostrar los resultados visualmente
#             guardar_imagenes (bool): Si guardar las imágenes procesadas
            
#         Returns:
#             dict: Resultados del procesamiento
#         """
#         resultados = {
#             'archivo': ruta_pdf,
#             'paginas_procesadas': 0,
#             'total_lineas': 0,
#             'total_pentagramas': 0,
#             'detalles_por_pagina': []
#         }
        
#         # Convertir PDF a imágenes
#         imagenes = self.pdf_a_imagenes(ruta_pdf)
#         if not imagenes:
#             return resultados
        
#         for i, imagen_pil in enumerate(imagenes):
#             print(f"\n🔍 Procesando página {i+1}/{len(imagenes)}...")
            
#             # Preprocesar imagen
#             imagen_gris, imagen_binaria = self.preprocesar_imagen(imagen_pil)
            
#             # Detectar líneas horizontales
#             lineas, imagen_lineas = self.detectar_lineas_horizontales(imagen_binaria)
            
#             # Agrupar en pentagramas
#             pentagramas = self.agrupar_pentagramas(lineas)
            
#             # Guardar resultados de esta página
#             detalle_pagina = {
#                 'pagina': i + 1,
#                 'lineas_detectadas': len(lineas),
#                 'pentagramas_detectados': len(pentagramas),
#                 'lineas': lineas,
#                 'pentagramas': pentagramas
#             }
            
#             resultados['detalles_por_pagina'].append(detalle_pagina)
#             resultados['total_lineas'] += len(lineas)
#             resultados['total_pentagramas'] += len(pentagramas)
            
#             print(f"   📏 Líneas detectadas: {len(lineas)}")
#             print(f"   🎼 Pentagramas detectados: {len(pentagramas)}")
            
#             # Mostrar resultados si se solicita
#             if mostrar_resultados:
#                 self.visualizar_resultados(
#                     imagen_gris, lineas, pentagramas, 
#                     f"Página {i+1}"
#                 )
            
#             # Guardar imágenes si se solicita
#             if guardar_imagenes:
#                 nombre_base = Path(ruta_pdf).stem
#                 cv2.imwrite(f"{nombre_base}_pagina_{i+1}_original.png", imagen_gris)
#                 cv2.imwrite(f"{nombre_base}_pagina_{i+1}_lineas.png", imagen_lineas)
        
#         resultados['paginas_procesadas'] = len(imagenes)
#         return resultados
    
#     def imprimir_reporte(self, resultados):
#         """
#         Imprime un reporte detallado de los resultados
        
#         Args:
#             resultados (dict): Resultados del procesamiento
#         """
#         print("\n" + "="*60)
#         print("📊 REPORTE DE ANÁLISIS DE PARTITURA")
#         print("="*60)
#         print(f"📄 Archivo: {resultados['archivo']}")
#         print(f"📚 Páginas procesadas: {resultados['paginas_procesadas']}")
#         print(f"📏 Total de líneas detectadas: {resultados['total_lineas']}")
#         print(f"🎼 Total de pentagramas detectados: {resultados['total_pentagramas']}")
        
#         print(f"\n📋 Detalle por página:")
#         print("-" * 40)
        
#         for detalle in resultados['detalles_por_pagina']:
#             print(f"   Página {detalle['pagina']:2d}: "
#                   f"{detalle['lineas_detectadas']:3d} líneas, "
#                   f"{detalle['pentagramas_detectados']:2d} pentagramas")
        
#         if resultados['total_pentagramas'] > 0:
#             promedio_lineas = resultados['total_lineas'] / resultados['total_pentagramas']
#             print(f"\n📈 Promedio de líneas por pentagrama: {promedio_lineas:.1f}")

# def main():
#     """Función principal"""
#     reconocedor = ReconocedorLineasPartitura()
    
#     # Lista de archivos PDF a buscar
#     archivos_candidatos = [
#         "Oblivion_A.pdf",
#         "iniciales.pdf", 
#         "iniciales-4.pdf"
#     ]
    
#     # Si se proporciona un archivo como argumento
#     if len(sys.argv) > 1:
#         archivo_pdf = sys.argv[1]
#         if not Path(archivo_pdf).exists():
#             print(f"❌ Error: El archivo '{archivo_pdf}' no existe")
#             return
        
#         print(f"🎯 Procesando archivo especificado: {archivo_pdf}")
#         resultados = reconocedor.procesar_pdf(archivo_pdf)
#         reconocedor.imprimir_reporte(resultados)
#         return
    
#     # Buscar archivos automáticamente
#     print("🔍 Buscando archivos PDF de partituras...")
    
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
#         resultados = reconocedor.procesar_pdf(archivo_encontrado)
#         reconocedor.imprimir_reporte(resultados)
#     else:
#         print("\n❌ No se encontraron archivos PDF de partituras")
#         print("💡 Uso: python reconocer_lineas_partitura.py <archivo.pdf>")
#         print("📂 Archivos buscados:", ", ".join(archivos_candidatos))

# if __name__ == "__main__":
#     main()
