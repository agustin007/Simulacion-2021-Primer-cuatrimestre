import random
import sorting
import matplotlib.pyplot as plt
from soporte.helper import *


class ControladorGeneradorNumerosPseudoaleatorios:

    def generar_numeros_pseudoaleatorios_congruencial_lineal(self, cantidad, semilla, a, c, m):

        # Genero lista de numeros aleatorios
        numeros_generados = []
        xi = semilla
        for _ in range(0, cantidad):
            xi = truncar((a * xi + c) % m, 4)
            numero_pseualeatorio = truncar(xi / m, 4)
            numeros_generados.append(numero_pseualeatorio)

        return numeros_generados

    def generar_numeros_pseudoaleatorios_congruencial_multiplicativo(self, cantidad, semilla, a, m):

        # Genero lista de numeros aleatorios
        numeros_generados = []
        xi = semilla
        for _ in range(0, cantidad):
            xi = truncar((a * xi) % m, 4)
            numero_pseualeatorio = truncar(xi / m, 4)
            numeros_generados.append(numero_pseualeatorio)

        return numeros_generados

    def generar_numeros_pseudoaleatorios_provisto_por_lenguaje(self, cantidad):

        # Genero lista de numeros aleatorios
        numeros_generados = []
        for _ in range(0, cantidad):
            numero_pseualeatorio = truncar(random.random(), 4)
            numeros_generados.append(numero_pseualeatorio)

        return numeros_generados

    def obtener_intervalos(self, cantidad_intervalos):

        # Defino mínimo y máximo
        minimo = 0
        maximo = 1

        # Genero lista de intervalos
        intervalos = []
        max_intervalo = minimo
        paso = Decimal((maximo - minimo) / cantidad_intervalos).quantize(SIXPLACES)
        for i in range(0, cantidad_intervalos):
            min_intervalo = Decimal(max_intervalo).quantize(SIXPLACES)
            max_intervalo = Decimal(min_intervalo + paso).quantize(SIXPLACES)
            intervalos.append((min_intervalo, max_intervalo))

        return intervalos

    def generar_histograma(self, numeros_pseudoaleatorios, intervalos):

        # Defino mínimo y máximo
        minimo = 0
        maximo = 1

        # Creo grafico
        fig, ax = plt.subplots()

        cantidad_intervalos = len(intervalos)
        n_bins = cantidad_intervalos
        x = numeros_pseudoaleatorios

        ax.hist(x, n_bins, range=(minimo, maximo), rwidth=0.8, color="navy", label="Frecuencias observadas")
        ax.legend(prop={"size": 8})
        ax.set_title("Histograma")

        xticks = []
        xticks_labels = []
        for intervalo in intervalos:
            media = (intervalo[0] + intervalo[1]) / 2
            xticks.append(media)
            if cantidad_intervalos <= 10:
                xticks_labels.append(str(round(media, 2)))
            else:
                xticks_labels.append(str(round(media, 3)))
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticks_labels, rotation=45)

        plt.xlabel("Valores")
        plt.ylabel("Cantidad")
        plt.show()

    def realizar_test_chi_cuadrado(self, numeros_pseudoaleatorios, intervalos):

        # Ordeno lista de numeros pseudoaleatorios para facilitar el calculo de frecuencias por intervalo, optimizando
        # el procesamiento con un algoritmo de ordenamiento de O(n * log n)
        numeros_pseudoaleatorios = sorting.merge(numeros_pseudoaleatorios)

        # Calculo frecuencias observadas por intervalo
        cantidad_intervalos = len(intervalos)
        frecuencias_observadas_x_intervalo = [0] * cantidad_intervalos
        index = 0
        for numero_pseudoaleatorio in numeros_pseudoaleatorios:
            if not (intervalos[index][0] <= numero_pseudoaleatorio < intervalos[index][1]):
                index += 1
            frecuencias_observadas_x_intervalo[index] += 1

        # Calculo frecuencias esperadas por intervalo
        fe = Decimal(len(numeros_pseudoaleatorios) / cantidad_intervalos)
        frecuencias_esperadas_x_intervalo = [fe] * cantidad_intervalos

        # Genero una lista de diccionarios con el calculo de la prueba de chi cuadrado por intervalo y guardo el final
        # en una variable
        chi_cuadrado_x_intervalo = []
        fo_acum = 0
        fe_acum = 0
        c_acum = 0
        for i in range(0, cantidad_intervalos):
            intervalo = (intervalos[i][0].quantize(TWOPLACES), intervalos[i][1].quantize(TWOPLACES))
            fo = frecuencias_observadas_x_intervalo[i]
            fo_acum += fo
            fe = frecuencias_esperadas_x_intervalo[i]
            fe_acum += fe
            c = ((fo - fe) ** 2) / fe
            c_acum += c
            chi_cuadrado_x_intervalo.append({
                "intervalo": intervalo,
                "fo": fo,
                "fo_acum": round(fo_acum, 4),
                "fe": fe.quantize(FOURPLACES),
                "fe_acum": round(fe_acum, 4),
                "c": c.quantize(FOURPLACES),
                "c_acum": round(c_acum, 4)
            })
        chi_cuadrado = round(c_acum, 4)

        return chi_cuadrado_x_intervalo, chi_cuadrado

