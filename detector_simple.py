# #!/usr/bin/env python3
# """
# Detector simple de líneas de pentagrama en PDFs
# Versión simplificada para detección rápida
# """

# import cv2
# import numpy as np
# from pdf2image import convert_from_path
# import sys
# from pathlib import Path

# def detectar_lineas_simples(ruta_pdf):
#     """
#     Función simple para detectar líneas de pentagrama
    
#     Args:
#         ruta_pdf (str): Ruta al archivo PDF
#     """
    
#     print(f"🔍 Analizando: {ruta_pdf}")
    
#     try:
#         # Convertir PDF a imagen (solo primera página)
#         imagenes = convert_from_path(ruta_pdf, dpi=200, first_page=1, last_page=1)
        
#         if not imagenes:
#             print("❌ No se pudo convertir el PDF")
#             return
        
#         # Tomar la primera página
#         imagen_pil = imagenes[0]
        
#         # Convertir a OpenCV
#         imagen = cv2.cvtColor(np.array(imagen_pil), cv2.COLOR_RGB2BGR)
#         gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        
#         # Binarizar la imagen
#         _, binaria = cv2.threshold(gris, 128, 255, cv2.THRESH_BINARY_INV)
        
#         # Detectar líneas horizontales usando HoughLinesP
#         lineas = cv2.HoughLinesP(
#             binaria, 
#             rho=1, 
#             theta=np.pi/180, 
#             threshold=100, 
#             minLineLength=200, 
#             maxLineGap=10
#         )
        
#         if lineas is not None:
#             # Filtrar solo líneas horizontales (ángulo cercano a 0)
#             lineas_horizontales = []
            
#             for linea in lineas:
#                 x1, y1, x2, y2 = linea[0]
                
#                 # Calcular ángulo de la línea
#                 angulo = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                
#                 # Filtrar líneas horizontales (ángulo entre -10 y 10 grados)
#                 if abs(angulo) < 10:
#                     lineas_horizontales.append((x1, y1, x2, y2))
            
#             print(f"📏 Líneas horizontales detectadas: {len(lineas_horizontales)}")
            
#             # Agrupar líneas por proximidad (pentagramas)
#             lineas_ordenadas = sorted(lineas_horizontales, key=lambda l: l[1])
            
#             pentagramas = []
#             grupo_actual = []
            
#             for i, linea in enumerate(lineas_ordenadas):
#                 if i == 0:
#                     grupo_actual = [linea]
#                 else:
#                     # Distancia a la línea anterior
#                     distancia = abs(linea[1] - lineas_ordenadas[i-1][1])
                    
#                     if distancia < 50:  # Líneas del mismo pentagrama
#                         grupo_actual.append(linea)
#                     else:  # Nuevo pentagrama
#                         if len(grupo_actual) >= 4:
#                             pentagramas.append(grupo_actual)
#                         grupo_actual = [linea]
            
#             # Agregar último grupo
#             if len(grupo_actual) >= 4:
#                 pentagramas.append(grupo_actual)
            
#             print(f"🎼 Pentagramas detectados: {len(pentagramas)}")
            
#             # Mostrar detalles de cada pentagrama
#             for i, pentagrama in enumerate(pentagramas):
#                 print(f"   Pentagrama {i+1}: {len(pentagrama)} líneas")
#                 for j, (x1, y1, x2, y2) in enumerate(pentagrama):
#                     print(f"     Línea {j+1}: Y={y1}, Longitud={x2-x1}")
            
#             # Crear imagen de resultado
#             resultado = imagen.copy()
            
#             # Dibujar líneas detectadas
#             for i, pentagrama in enumerate(pentagramas):
#                 # Color diferente para cada pentagrama
#                 color = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)][i % 5]
                
#                 for x1, y1, x2, y2 in pentagrama:
#                     cv2.line(resultado, (x1, y1), (x2, y2), color, 3)
            
#             # Guardar resultado
#             nombre_salida = f"{Path(ruta_pdf).stem}_lineas_detectadas.png"
#             cv2.imwrite(nombre_salida, resultado)
#             print(f"💾 Imagen guardada: {nombre_salida}")
            
#         else:
#             print("❌ No se detectaron líneas")
            
#     except Exception as e:
#         print(f"❌ Error: {e}")

# def main():
#     """Función principal simplificada"""
    
#     if len(sys.argv) > 1:
#         archivo = sys.argv[1]
#         if Path(archivo).exists():
#             detectar_lineas_simples(archivo)
#         else:
#             print(f"❌ Archivo no encontrado: {archivo}")
#     else:
#         # Buscar archivos PDF en el directorio actual
#         archivos_pdf = list(Path(".").glob("*.pdf"))
        
#         if archivos_pdf:
#             print(f"📁 Archivos PDF encontrados: {len(archivos_pdf)}")
#             for pdf in archivos_pdf:
#                 print(f"   • {pdf}")
            
#             # Procesar el primer PDF encontrado
#             detectar_lineas_simples(str(archivos_pdf[0]))
#         else:
#             print("❌ No se encontraron archivos PDF")
#             print("💡 Uso: python detector_simple.py <archivo.pdf>")

# if __name__ == "__main__":
#     main()
