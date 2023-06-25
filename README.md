# Instalar anaconda o miniconda

    https://docs.conda.io/en/latest/miniconda.html

# Estableciendo el entorno virtual

Crear entorno virtual e instalar dependencias (solo la primera vez):

    make create-env

Activar entorno en terminal de VSCode y ejecutar dashboard:

    conda activate dz3

Ejecutar dashboard:
    
- Opción 1:
        
        make run

- Opción 2:

        python app.py

    
# Comandos:

En directorio raíz (Dashboard):

- Generar SOLO dashboard: 
    python app.py

- Generar dashboard y reporte diario: 
    python app.py --daily

- Generar dashboard y reporte mensual: 
    python app.py --monthly

- Generar dashboard, reporte diario y mensual: 
    python app.py --daily --monthly

**Opcional**: Si se tiene guardada la página en un archivo url.html y se quiere leer los datos desde ahí, cambiar valor *url_from_file* en config.yaml, a True.
Usar un archivo ya guardado en lugar de leer la web cada vez que se genere el dashboard, siempre tomará menos tiempo.


