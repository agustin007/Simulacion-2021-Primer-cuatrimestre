import random
from copy import deepcopy
from soporte.helper import *


class ControladorSistemaColas:

    # Atributos
    tiempo_autos = None
    probabilidad_chico_autos = None
    probabilidad_grande_autos = None
    probabilidad_utilitario_autos = None
    probabilidad_1_tiempo_estacionamiento = None
    probabilidad_2_tiempo_estacionamiento = None
    probabilidad_3_tiempo_estacionamiento = None
    probabilidad_4_tiempo_estacionamiento = None
    tiempo_cobro = None

    ultimo_id_auto = 0

    # Constantes
    EVENTO_LLEGADA_AUTO = "llegada_auto"
    EVENTO_FIN_ESTACIONAMIENTO = "fin_estacionamiento"
    EVENTO_FIN_COBRADO = "fin_cobrado"

    ESTADO_LUGAR_ESTACIONAMIENTO_LIBRE = "Libre"
    ESTADO_LUGAR_ESTACIONAMIENTO_OCUPADO = "Ocupado"

    ESTADO_CABINA_COBRO_LIBRE = "Libre"
    ESTADO_CABINA_COBRO_OCUPADO = "Ocupado"

    ESTADO_AUTO_ESTACIONADO = "Estacionado"
    ESTADO_AUTO_ESPERANDO_PAGAR = "Esperando pagar"
    ESTADO_AUTO_PAGANDO = "Pagando"

    TIPO_AUTO_CHICO = "Chico"
    TIPO_AUTO_GRANDE = "Grande"
    TIPO_AUTO_UTILITARIO = "Utilitario"

    def simular_iteracion(self, vector_estado, destruir_objetos_temporales=True):

        # Copio vector estado anterior para realizar las acciones necesarias de esta iteración sin modificar el anterior
        vector_estado = deepcopy(vector_estado)

        # Quito datos auxiliares de demás eventos innecesarios para nuevo vector estado
        vector_estado["eventos"]["llegada_autos"]["rnd_tiempo_entre_llegadas"] = None
        vector_estado["eventos"]["llegada_autos"]["tiempo_proxima_llegada"] = None
        vector_estado["eventos"]["fin_estacionamiento"]["rnd_fin_estacionamiento"] = None
        vector_estado["eventos"]["fin_estacionamiento"]["tiempo_estacionado"] = None
        vector_estado["eventos"]["fin_cobrado"]["tiempo_cobrado"] = None
        vector_estado["clientes"]["auxiliares"]["rnd_tipo_auto"] = None
        vector_estado["clientes"]["auxiliares"]["tipo_auto"] = None

        # Obtengo siguiente evento a procesar
        evento = None
        reloj_evento = None
        id_servidor_a_liberar = None

        proxima_llegada = vector_estado.get("eventos").get("llegada_autos").get("proxima_llegada")
        if proxima_llegada is not None:
            evento = self.EVENTO_LLEGADA_AUTO
            reloj_evento = proxima_llegada

        for fin_tiempo_estacionado_dict in vector_estado.get("eventos").get("fin_estacionamiento").get(
                "fines_tiempo_estacionado"):
            fin_tiempo_estacionado = fin_tiempo_estacionado_dict.get("fin_tiempo_estacionado")
            if reloj_evento is None or \
                    fin_tiempo_estacionado is not None and fin_tiempo_estacionado < reloj_evento:
                id_lugar_estacionamiento = fin_tiempo_estacionado_dict.get("id_lugar_estacionamiento")
                evento = self.EVENTO_FIN_ESTACIONAMIENTO
                reloj_evento = fin_tiempo_estacionado
                id_servidor_a_liberar = id_lugar_estacionamiento

        for fin_tiempo_cobrado_dict in vector_estado.get("eventos").get("fin_cobrado").get(
                "fines_tiempo_cobrado"):
            fin_tiempo_cobrado = fin_tiempo_cobrado_dict.get("fin_tiempo_cobrado")
            if reloj_evento is None or \
                    fin_tiempo_cobrado is not None and fin_tiempo_cobrado < reloj_evento:
                id_cabina_cobro = fin_tiempo_cobrado_dict.get("id_cabina_cobro")
                evento = self.EVENTO_FIN_COBRADO
                reloj_evento = fin_tiempo_cobrado
                id_servidor_a_liberar = id_cabina_cobro

        # Seteo nuevo evento en vector
        vector_estado["reloj"] = reloj_evento
        vector_estado["evento"] = evento
        if id_servidor_a_liberar is not None:
            vector_estado["evento"] += " (" + str(id_servidor_a_liberar) + ")"

        # Realizo acciones dependiendo del evento

        # Evento llegada_autos
        if evento == self.EVENTO_LLEGADA_AUTO:

            # Aumento contador de ids de auto
            self.ultimo_id_auto += 1

            # Completo datos de evento sabiendo a que auto se refiere
            vector_estado["evento"] += " (" + str(self.ultimo_id_auto) + ")"

            # Genero próxima llegada
            rnd_tiempo_entre_llegadas = truncar(random.random(), 2)
            tiempo_proxima_llegada = round(-1 * self.tiempo_autos * math.log(1 - rnd_tiempo_entre_llegadas), 2)
            proxima_llegada = reloj_evento + tiempo_proxima_llegada

            # Seteo datos de próxima llegada en vector estado
            vector_estado["eventos"]["llegada_autos"]["rnd_tiempo_entre_llegadas"] = rnd_tiempo_entre_llegadas
            vector_estado["eventos"]["llegada_autos"]["tiempo_proxima_llegada"] = tiempo_proxima_llegada
            vector_estado["eventos"]["llegada_autos"]["proxima_llegada"] = proxima_llegada

            # Verifico si existe al menos algún lugar del estacionamiento libre, para pasarlo a ocupado
            id_lugar_estacionamiento_encontrado = None
            for lugar_estacionamiento_dict in vector_estado.get("sevidores").get("lugares_estacionamiento"):
                estado_lugar_estacionamiento = lugar_estacionamiento_dict.get("estado")
                if estado_lugar_estacionamiento == self.ESTADO_LUGAR_ESTACIONAMIENTO_LIBRE:
                    id_lugar_estacionamiento_encontrado = lugar_estacionamiento_dict.get("id")
                    lugar_estacionamiento_dict["estado"] = self.ESTADO_LUGAR_ESTACIONAMIENTO_OCUPADO
                    break

            # Si se encontró lugar de estacionamiento
            if id_lugar_estacionamiento_encontrado is not None:

                # Genero fin estacionamiento para el auto recién llegado
                rnd_fin_estacionamiento = truncar(random.random(), 2)
                limite_tiempo_estacionamiento_1 = self.probabilidad_1_tiempo_estacionamiento / 100
                limite_tiempo_estacionamiento_2 = limite_tiempo_estacionamiento_1 \
                                                  + self.probabilidad_2_tiempo_estacionamiento / 100
                limite_tiempo_estacionamiento_3 = limite_tiempo_estacionamiento_2 \
                                                  + self.probabilidad_3_tiempo_estacionamiento / 100
                if 0 <= rnd_fin_estacionamiento < limite_tiempo_estacionamiento_1:
                    tiempo_estacionado = 1
                elif limite_tiempo_estacionamiento_1 <= rnd_fin_estacionamiento < limite_tiempo_estacionamiento_2:
                    tiempo_estacionado = 2
                elif limite_tiempo_estacionamiento_2 <= rnd_fin_estacionamiento < limite_tiempo_estacionamiento_3:
                    tiempo_estacionado = 3
                else:
                    tiempo_estacionado = 4
                fin_tiempo_estacionado = reloj_evento + tiempo_estacionado

                # Seteo datos de fin tiempo estacionado
                vector_estado["eventos"]["fin_estacionamiento"]["rnd_fin_estacionamiento"] = rnd_fin_estacionamiento
                vector_estado["eventos"]["fin_estacionamiento"]["tiempo_estacionado"] = tiempo_estacionado
                for fin_tiempo_estacionado_dict in vector_estado.get("eventos").get("fin_estacionamiento").get(
                        "fines_tiempo_estacionado"):
                    id_lugar_estacionamiento = fin_tiempo_estacionado_dict.get("id_lugar_estacionamiento")
                    if id_lugar_estacionamiento == id_lugar_estacionamiento_encontrado:
                        fin_tiempo_estacionado_dict["fin_tiempo_estacionado"] = fin_tiempo_estacionado
                        break

                # Genero auxiliares para generación de auto
                rnd_tipo_auto = truncar(random.random(), 2)
                limite_autos_chico = self.probabilidad_chico_autos / 100
                limite_autos_grande = limite_autos_chico + self.probabilidad_grande_autos / 100
                if 0 <= rnd_tipo_auto < limite_autos_chico:
                    tipo_auto = self.TIPO_AUTO_CHICO
                elif limite_autos_chico <= rnd_tipo_auto < limite_autos_grande:
                    tipo_auto = self.TIPO_AUTO_GRANDE
                else:
                    tipo_auto = self.TIPO_AUTO_UTILITARIO

                # Seteo datos auxiliares para geneación de auto
                vector_estado["clientes"]["auxiliares"]["rnd_tipo_auto"] = rnd_tipo_auto
                vector_estado["clientes"]["auxiliares"]["tipo_auto"] = tipo_auto

                # Genero auto con sus atributos correspondientes
                id_auto = self.ultimo_id_auto
                estado_auto = self.ESTADO_AUTO_ESTACIONADO
                id_lugar_estacionamiento_auto = id_lugar_estacionamiento_encontrado
                id_cabina_cobro_auto = None
                hora_inicio_espera_para_pagar_auto = None
                if tipo_auto == self.TIPO_AUTO_CHICO:
                    monto_auto = 50 * tiempo_estacionado
                elif tipo_auto == self.TIPO_AUTO_GRANDE:
                    monto_auto = 80 * tiempo_estacionado
                else:
                    monto_auto = 100 * tiempo_estacionado
                vector_estado.get("clientes").get("autos").append({
                    "id": id_auto,
                    "estado": estado_auto,
                    "id_lugar_estacionamiento": id_lugar_estacionamiento_auto,
                    "id_cabina_cobro": id_cabina_cobro_auto,
                    "hora_inicio_espera_para_pagar": hora_inicio_espera_para_pagar_auto,
                    "monto": monto_auto
                })

                # Seteo datos de contadores
                vector_estado["contadores"]["lugares_estacionamiento_ocupados"] += 1
                porcentaje_ocupacion = round(vector_estado.get("contadores").get("lugares_estacionamiento_ocupados")
                                             * 100 / 20, 2)
                vector_estado["contadores"]["porcentaje_ocupacion"] = porcentaje_ocupacion

            # Si no se encontró lugar de estacionamiento
            else:

                # Seteo datos de contadores
                vector_estado["contadores"]["autos_rechazados"] += 1

        # Evento fin_estacionamiento
        elif evento == self.EVENTO_FIN_ESTACIONAMIENTO:

            # Borro dato de fin de estacionamiento
            for fin_tiempo_estacionado_dict in vector_estado.get("eventos").get("fin_estacionamiento").get(
                    "fines_tiempo_estacionado"):
                fin_tiempo_estacionado = fin_tiempo_estacionado_dict.get("fin_tiempo_estacionado")
                if reloj_evento == fin_tiempo_estacionado:
                    fin_tiempo_estacionado_dict["fin_tiempo_estacionado"] = None
                    break

            # Verifico si existe al menos algúna cabina de cobro libre, para pasarla a ocupada o agregar cola a la que
            # menos tenga
            id_cabina_cobro_encontrada = None
            id_cabina_con_menos_cola = None
            cola_cabina_con_menos_cola = None
            for cabina_cobro_dict in vector_estado.get("sevidores").get("cabinas_cobro"):
                estado_cabina_cobro = cabina_cobro_dict.get("estado")
                if estado_cabina_cobro == self.ESTADO_CABINA_COBRO_LIBRE:
                    id_cabina_cobro_encontrada = cabina_cobro_dict.get("id")
                    cabina_cobro_dict["estado"] = self.ESTADO_CABINA_COBRO_OCUPADO
                    break
                else:
                    cola_cabina_cobro = cabina_cobro_dict.get("cola")
                    if id_cabina_con_menos_cola is None or cola_cabina_cobro < cola_cabina_con_menos_cola:
                        id_cabina_con_menos_cola = cabina_cobro_dict.get("id")
                        cola_cabina_con_menos_cola = cola_cabina_cobro

            # Si se encontró cabina de cobro
            if id_cabina_cobro_encontrada is not None:

                # Genero fin cobrado para el auto que recién termina su estacionamiento
                tiempo_cobrado = 2
                fin_tiempo_cobrado = reloj_evento + tiempo_cobrado

                # Seteo datos de fin cobrado
                vector_estado["eventos"]["fin_cobrado"]["tiempo_cobrado"] = tiempo_cobrado
                for fin_tiempo_cobrado_dict in vector_estado.get("eventos").get("fin_cobrado").get(
                        "fines_tiempo_cobrado"):
                    id_cabina_cobro = fin_tiempo_cobrado_dict.get("id_cabina_cobro")
                    if id_cabina_cobro == id_cabina_cobro_encontrada:
                        fin_tiempo_cobrado_dict["fin_tiempo_cobrado"] = fin_tiempo_cobrado
                        break

                # Seteo datos de lugar de estacionamiento, ya que se desocupa el lugar
                for lugar_estacionamiento_dict in vector_estado.get("sevidores").get("lugares_estacionamiento"):
                    id_lugar_estacionamiento = lugar_estacionamiento_dict.get("id")
                    if id_lugar_estacionamiento == id_servidor_a_liberar:
                        lugar_estacionamiento_dict["estado"] = self.ESTADO_LUGAR_ESTACIONAMIENTO_LIBRE
                        break

                # Seteo datos del auto, ya que cambia el estado
                for auto_dict in vector_estado.get("clientes").get("autos"):
                    id_lugar_estacionamiento = auto_dict.get("id_lugar_estacionamiento")
                    if id_lugar_estacionamiento == id_servidor_a_liberar:
                        auto_dict["estado"] = self.ESTADO_AUTO_PAGANDO
                        auto_dict["id_cabina_cobro"] = id_cabina_cobro_encontrada
                        break

                # Seteo datos de contadores
                vector_estado["contadores"]["lugares_estacionamiento_ocupados"] -= 1
                porcentaje_ocupacion = round(vector_estado.get("contadores").get("lugares_estacionamiento_ocupados")
                                             * 100 / 20, 2)
                vector_estado["contadores"]["porcentaje_ocupacion"] = porcentaje_ocupacion

            # Si no se encontró cabina de cobro
            else:

                # Seteo datos de cabina de cobro, ya que se agrega un auto a la cola
                for cabina_cobro_dict in vector_estado.get("sevidores").get("cabinas_cobro"):
                    id_cabina_cobro = cabina_cobro_dict.get("id")
                    if id_cabina_cobro == id_cabina_con_menos_cola:
                        cabina_cobro_dict["cola"] = cola_cabina_con_menos_cola + 1
                        break

                # Seteo datos del auto, ya que cambia el estado
                for auto_dict in vector_estado.get("clientes").get("autos"):
                    id_lugar_estacionamiento = auto_dict.get("id_lugar_estacionamiento")
                    if id_lugar_estacionamiento == id_servidor_a_liberar:
                        auto_dict["hora_inicio_espera_para_pagar"] = reloj_evento
                        auto_dict["estado"] = self.ESTADO_AUTO_ESPERANDO_PAGAR
                        break

        elif evento == self.EVENTO_FIN_COBRADO:

            # Borro dato de fin de estacionamiento
            for fin_tiempo_cobrado_dict in vector_estado.get("eventos").get("fin_cobrado").get(
                    "fines_tiempo_cobrado"):
                fin_tiempo_cobrado = fin_tiempo_cobrado_dict.get("fin_tiempo_cobrado")
                if reloj_evento == fin_tiempo_cobrado:
                    fin_tiempo_cobrado_dict["fin_tiempo_cobrado"] = None
                    break

            # Seteo datos de cabina de cobro, ya que cambia de estado o disminuye la cola
            id_cabina_cobro_con_cola_encontrada = None
            for cabina_cobro_dict in vector_estado.get("sevidores").get("cabinas_cobro"):
                id_cabina_cobro = cabina_cobro_dict.get("id")
                if id_cabina_cobro == id_servidor_a_liberar:
                    cola_cabina_cobro = cabina_cobro_dict.get("cola")
                    if cola_cabina_cobro == 0:
                        cabina_cobro_dict["estado"] = self.ESTADO_CABINA_COBRO_LIBRE
                    else:
                        cabina_cobro_dict["cola"] -= 1
                        id_cabina_cobro_con_cola_encontrada = id_cabina_cobro
                    break

            # Seteo datos del auto, ya que debe destruirse
            monto_auto = None
            indice_auto = 0
            for auto_dict in vector_estado.get("clientes").get("autos"):
                id_cabina_cobro = auto_dict.get("id_cabina_cobro")
                if id_cabina_cobro == id_servidor_a_liberar:
                    monto_auto = auto_dict.get("monto")
                    break
                indice_auto += 1
            vector_estado["clientes"]["autos"][indice_auto]["estado"] = None
            vector_estado["clientes"]["autos"][indice_auto]["id_lugar_estacionamiento"] = None
            vector_estado["clientes"]["autos"][indice_auto]["id_cabina_cobro"] = None
            vector_estado["clientes"]["autos"][indice_auto]["hora_inicio_espera_para_pagar"] = None
            vector_estado["clientes"]["autos"][indice_auto]["monto"] = None
            if destruir_objetos_temporales:
                del vector_estado.get("clientes").get("autos")[indice_auto]

            # Seteo datos de contadores
            vector_estado["contadores"]["monto_recaudado"] += monto_auto

            # Si se encontró cola en la cabia de cobro
            if id_cabina_cobro_con_cola_encontrada is not None:

                # Busco el auto que sigue para pagar y su lugar de estacionamiento
                id_auto_con_menos_hora_inicio_espera = None
                hora_inicio_espera_auto_con_menos_hora_inicio_espera = None
                id_lugar_estacionamiento_auto_con_menos_hora_inicio_espera = None
                for auto_dict in vector_estado.get("clientes").get("autos"):
                    estado_auto = auto_dict.get("estado")
                    if estado_auto == self.ESTADO_AUTO_ESPERANDO_PAGAR:
                        hora_inicio_espera = auto_dict.get("hora_inicio_espera_para_pagar")
                        if id_auto_con_menos_hora_inicio_espera is None or \
                                hora_inicio_espera < hora_inicio_espera_auto_con_menos_hora_inicio_espera:
                            id_auto_con_menos_hora_inicio_espera = auto_dict.get("id")
                            id_lugar_estacionamiento_auto_con_menos_hora_inicio_espera = \
                                auto_dict.get("id_lugar_estacionamiento")
                            hora_inicio_espera_auto_con_menos_hora_inicio_espera = hora_inicio_espera

                # Genero fin cobrado para el auto que sigue para pagar
                tiempo_cobrado = 2
                fin_tiempo_cobrado = reloj_evento + tiempo_cobrado

                # Seteo datos de fin cobrado para el auto que sigue para pagar
                vector_estado["eventos"]["fin_cobrado"]["tiempo_cobrado"] = tiempo_cobrado
                for fin_tiempo_cobrado_dict in vector_estado.get("eventos").get("fin_cobrado").get(
                        "fines_tiempo_cobrado"):
                    id_cabina_cobro = fin_tiempo_cobrado_dict.get("id_cabina_cobro")
                    if id_cabina_cobro == id_cabina_cobro_con_cola_encontrada:
                        fin_tiempo_cobrado_dict["fin_tiempo_cobrado"] = fin_tiempo_cobrado
                        break

                # Seteo datos de lugar de estacionamiento, ya que se desocupa el lugar
                for lugar_estacionamiento_dict in vector_estado.get("sevidores").get(
                        "lugares_estacionamiento"):
                    id_lugar_estacionamiento = lugar_estacionamiento_dict.get("id")
                    if id_lugar_estacionamiento == id_lugar_estacionamiento_auto_con_menos_hora_inicio_espera:
                        lugar_estacionamiento_dict["estado"] = self.ESTADO_LUGAR_ESTACIONAMIENTO_LIBRE
                        break

                # Seteo datos del auto, ya que cambia el estado
                for auto_dict in vector_estado.get("clientes").get("autos"):
                    id_lugar_estacionamiento = auto_dict.get("id_lugar_estacionamiento")
                    if id_lugar_estacionamiento == id_lugar_estacionamiento_auto_con_menos_hora_inicio_espera:
                        auto_dict["estado"] = self.ESTADO_AUTO_PAGANDO
                        auto_dict["id_cabina_cobro"] = id_cabina_cobro_con_cola_encontrada
                        break

                # Seteo datos de contadores
                vector_estado["contadores"]["lugares_estacionamiento_ocupados"] -= 1
                porcentaje_ocupacion = round(
                    vector_estado.get("contadores").get("lugares_estacionamiento_ocupados")
                    * 100 / 20, 2)
                vector_estado["contadores"]["porcentaje_ocupacion"] = porcentaje_ocupacion

        return vector_estado

    def simular_iteraciones(self, tiempo_simulacion, tiempo_desde, cantidad_iteraciones, tiempo_autos,
                            probabilidad_chico_autos, probabilidad_grande_autos, probabilidad_utilitario_autos,
                            probabilidad_1_tiempo_estacionamiento, probabilidad_2_tiempo_estacionamiento,
                            probabilidad_3_tiempo_estacionamiento, probabilidad_4_tiempo_estacionamiento,
                            cantidad_cabinas_cobro, tiempo_cobro):

        # Agrego datos como atributos del objeto para poder manejarlos a nivel clase
        self.tiempo_autos = tiempo_autos
        self.probabilidad_chico_autos = probabilidad_chico_autos
        self.probabilidad_grande_autos = probabilidad_grande_autos
        self.probabilidad_utilitario_autos = probabilidad_utilitario_autos
        self.probabilidad_1_tiempo_estacionamiento = probabilidad_1_tiempo_estacionamiento
        self.probabilidad_2_tiempo_estacionamiento = probabilidad_2_tiempo_estacionamiento
        self.probabilidad_3_tiempo_estacionamiento = probabilidad_3_tiempo_estacionamiento
        self.probabilidad_4_tiempo_estacionamiento = probabilidad_4_tiempo_estacionamiento
        self.tiempo_cobro = tiempo_cobro

        # Genero vector de estado inicial
        rnd_tiempo_entre_llegadas = truncar(random.random(), 2)
        tiempo_proxima_llegada = round(-1 * self.tiempo_autos * math.log(1 - rnd_tiempo_entre_llegadas), 2)
        proxima_llegada = tiempo_proxima_llegada
        vector_estado = {
            "evento": "inicializacion",
            "reloj": 0,
            "eventos": {
                "llegada_autos": {
                    "rnd_tiempo_entre_llegadas": rnd_tiempo_entre_llegadas,
                    "tiempo_proxima_llegada": tiempo_proxima_llegada,
                    "proxima_llegada": proxima_llegada,
                },
                "fin_estacionamiento": {
                    "rnd_fin_estacionamiento": None,
                    "tiempo_estacionado": None,
                    "fines_tiempo_estacionado": []
                },
                "fin_cobrado": {
                    "tiempo_cobrado": None,
                    "fines_tiempo_cobrado": []
                },
            },
            "servidores": {
                "lugares_estacionamiento": [],
                "cabinas_cobro": []
            },
            "contadores": {
                "autos_rechazados": 0,
                "lugares_estacionamiento_ocupados": 0,
                "porcentaje_ocupacion": 0,
                "monto_recaudado": 0,
            },
            "clientes": {
                "auxiliares": {
                    "rnd_tipo_auto": None,
                    "tipo_auto": None
                },
                "autos": []
            }
        }

        for i in range(1, 20 + 1):
            vector_estado.get("eventos").get("fin_estacionamiento").get("fines_tiempo_estacionado").append({
                "id_lugar_estacionamiento": i,
                "fin_tiempo_estacionado": None
            })
            vector_estado["servidores"]["lugares_estacionamiento"].append({
                "id": i,
                "estado": self.ESTADO_LUGAR_ESTACIONAMIENTO_LIBRE
            })
        for i in range(1, cantidad_cabinas_cobro + 1):
            vector_estado["eventos"]["fin_cobrado"]["fines_tiempo_cobrado"].append({
                "id_cabina_cobro": i,
                "fin_cobrado": None
            })
            vector_estado["servidores"]["cabinas_cobro"].append({
                "id": i,
                "estado": self.ESTADO_CABINA_COBRO_LIBRE,
                "cola": 0
            })

        # Realizo simulación almacenando los vectores estados de las iteraciones de interés
        iteraciones_simuladas = [vector_estado]
        vector_estado_agregado = True
        cantidad_iteraciones_agregadas = 0

        while 1:
            vector_estado_proximo = self.simular_iteracion(vector_estado)
            if vector_estado_proximo.get("reloj") > tiempo_simulacion:
                break
            vector_estado = vector_estado_proximo
            vector_estado_agregado = False

            if vector_estado.get("reloj") >= tiempo_desde and cantidad_iteraciones_agregadas < cantidad_iteraciones:
                vector_estado_agregado = True
                cantidad_iteraciones_agregadas += 1
                iteraciones_simuladas.append(vector_estado)

        if not vector_estado_agregado:
            iteraciones_simuladas.append(vector_estado)

        # Devuelvo iteraciones simuladas de interés
        return iteraciones_simuladas