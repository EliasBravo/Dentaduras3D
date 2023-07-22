
from PIL import Image
import torch
from pytorch3d.structures import Meshes
import trimesh
import pyvista as pv
import sys
from PIL import Image

def convertir(img_path):
    # Cargar el modelo con los pesos
    model = torch.hub.load('ultralytics/yolov5', 'custom', path='src/weights/best1.pt') 
    
    #Guardar la predicción
    # Cargar la imagen
    image = Image.open(img_path)
    # Realizar la detección en la imagen
    results = model(image)
    # Crear una lista para almacenar las coordenadas
    predictions0 = []

    clase_map = {
        0.0: 'tooth_inc_end',
        1.0: 'tooth_inc_nor',
        2.0: 'tooth_mol_end',
        3.0: 'tooth_mol_nor'
    }
    # Obtener las coordenadas de las detecciones
    for detection in results.xyxy[0]:
        x1, y1, x2, y2, conf, class_id, *_ = detection.tolist()
        width = x2 - x1
        height = y2 - y1
        nombre_clase = clase_map.get(class_id, 'desconocido')
        predictions0.append({'x': x1, 'y': y1, 'width': width, 'height': height, 'class': nombre_clase})

    predictions= {'predictions': predictions0}
    
    results.show()
    altura = image.height #Calcular la altura de la imagen para utilizarlo en un método siguiente
    coords_tooth_mol_nor = []
    coords_tooth_inc_nor = []
    coords_tooth_mol_end = []
    coords_tooth_inc_end = []
    # Obtener las coordenadas de los objetos detectados
    def filtrar_prediction(prediction, class_name):
        dientes_coords = []
        for prediction in predictions['predictions']:
            if prediction['class'] == class_name:
                x = prediction['x']
                y = prediction['y']
                width = prediction['width']
                height = prediction['height']
                dientes_coords.append([x, y, width, height])
        return dientes_coords
    
    # Almacenar las coordenadas según cada clase de diente
    coords_tooth_mol_nor = filtrar_prediction(predictions, 'tooth_mol_nor')
    coords_tooth_inc_nor = filtrar_prediction(predictions, 'tooth_inc_nor')
    coords_tooth_mol_end = filtrar_prediction(predictions, 'tooth_mol_end')
    coords_tooth_inc_end = filtrar_prediction(predictions, 'tooth_inc_end')

    # Crear mallas en la coordenada de cada diente
    def convertir_a_mallas(dientes_coords):
        # Crear una lista de mallas para los dientes
        meshes = []
        for coords in dientes_coords:
            # Obtener las coordenadas individuales
            x, y, width, height = coords

            # Calcular las coordenadas 3D relativas a partir de las coordenadas 2D
            # Puedes ajustar estos cálculos según tus necesidades
            vertices_3d = [
                [x, y, 0],
                [x + width, y, 0],
                [x + width, y + height, 0],
                [x, y + height, 0],
            ]
            vertices_3d = torch.tensor(vertices_3d, dtype=torch.float32)

            # Crear una malla a partir de las coordenadas 3D
            faces = [[0, 1, 2], [0, 2, 3]]  # Definir las caras de la malla
            faces = torch.tensor(faces, dtype=torch.int64)
            mesh = Meshes(verts=[vertices_3d], faces=[faces])

            # Agregar la malla a la lista de mallas
            meshes.append(mesh)
        return meshes
    
    # Almacenar las mallas 
    meshes_1 =  convertir_a_mallas(coords_tooth_mol_nor)
    meshes_2 =  convertir_a_mallas(coords_tooth_inc_nor)
    meshes_3 =  convertir_a_mallas(coords_tooth_mol_end)
    meshes_4 =  convertir_a_mallas(coords_tooth_inc_end)
    lista_mallas= [meshes_1, meshes_2, meshes_3, meshes_4]

    # Convertir las mallas en OBJs
    def convertir_a_obj(lista_mallas, lista_obj_file, ruta_salida):
        scene = trimesh.Scene()
        contador = 0
        def recorrer_malla(lista_mallas, c, obj_file):
            for i, malla in enumerate(lista_mallas):
                # Obtener los vértices de la malla
                vertices = malla.verts_packed()

                # Cargar el archivo OBJ del objeto a posicionar en la malla
                obj_file1 = obj_file[c]
                objeto_trimesh = trimesh.load(obj_file1)

                # Clonar la geometría del objeto para posicionar en la malla
                objeto_posicionado = objeto_trimesh.copy()

                # Iterar sobre los vértices de la malla y obtener el promedio de las coordenadas
                promedio_vertice = vertices.mean(dim=0)

                # Obtener las coordenadas del promedio del vértice
                x, y, z = promedio_vertice.tolist()
                # Verificar si la coordenada "y" es menor que el punto medio de la altura de la imagen
                if y > altura/2:
                    # Voltear el objeto en el eje y
                    objeto_posicionado.vertices[:, 1] = -objeto_posicionado.vertices[:, 1]
                # Posicionar el objeto en el promedio del vértice
                objeto_posicionado.apply_translation([x, y, z])
                nonlocal contador
                contador += 1
                print(contador)
                # Agregar el objeto a la escena
                scene.add_geometry(objeto_posicionado)

        recorrer_malla(lista_mallas[0], 0, lista_obj_file)
        recorrer_malla(lista_mallas[1], 1, lista_obj_file)
        recorrer_malla(lista_mallas[2], 2, lista_obj_file)
        recorrer_malla(lista_mallas[3], 3, lista_obj_file)
        # Exportar la escena a un archivo OBJ
        scene.export(ruta_salida, file_type='obj')
   
    # Ejecución
    ruta_salida = "src/obj/prueba25.obj"
    lista_obj_file = ["src/obj/tooth_0.obj", "src/obj/tooth_1.obj", "src/obj/tooth_2.obj", "src/obj/tooth_3.obj"]
    convertir_a_obj(lista_mallas, lista_obj_file, ruta_salida)
    # Cargar el OBJ final
    mesh = pv.read("src/obj/prueba25.obj")
    # Crear un trazador PyVista
    plotter = pv.Plotter()
    # Agregar la malla al trazador
    plotter.add_mesh(mesh)
    # Calcular la cantidad de cada tipo de diente
    count_tooth_mol_nor = len(coords_tooth_mol_nor)
    count_tooth_inc_nor = len(coords_tooth_inc_nor)
    count_tooth_mol_end = len(coords_tooth_mol_end)
    count_tooth_inc_end = len(coords_tooth_inc_end)

    # Crear la cadena de texto con los conteos
    def get_plural_or_singular(n, singular, plural):
        return singular if n == 1 else plural
    
    total_sano = count_tooth_mol_nor + count_tooth_inc_nor
    total_no_sano = count_tooth_mol_end + count_tooth_inc_end
    if total_sano == 1:
        verb_form_sano = "encontró"
        text_diente = "diente"
        text_sano = "sano"
    else:
        verb_form_sano = "encontraron"
        text_diente = "dientes"
        text_sano = "sanos"

    if total_no_sano == 1:
        verb_form_no_sano = "encontró"
        text_diente1 = "diente"
        text_no_sano = "no sano"
    else:
        verb_form_no_sano = "encontraron"
        text_diente1 = "dientes"
        text_no_sano = "no sanos"

    text_line = f"Se {verb_form_sano} {total_sano} {text_diente} {text_sano} ("
    text_line += f"{count_tooth_mol_nor} molar{get_plural_or_singular(count_tooth_mol_nor, '', 'es')} y "
    text_line += f"{count_tooth_inc_nor} no molar{get_plural_or_singular(count_tooth_inc_nor, '', 'es')}),\n"
    text_line += f"y se {verb_form_no_sano} {total_no_sano} {text_diente1} {text_no_sano} ("
    text_line += f"{count_tooth_mol_end} molar{get_plural_or_singular(count_tooth_mol_end, '', 'es')} y "
    text_line += f"{count_tooth_inc_end} no molar{get_plural_or_singular(count_tooth_inc_end, '', 'es')})."
    # Asignar el texto
    plotter.add_text(text_line, position="upper_left", font_size=16, color="black", font="arial")

    # Muestra el trazador PyVista
    plotter.show()

    


