# Para windows:

- Instalar Git
	
    https://git-scm.com/download/win

En la terminal de VSCode:

- Ejecutar el siguiente comando para ingresar correo asociado a Github:

	git config --global user.email "user@email.com"

- Ingresar a la carpeta Documentos y clonar repositorio Dashboard:
	
    git clone https://github.com/rosepb28/Dashboard.git

# Instalar anaconda o miniconda, buscar versión 3.8 de Python

    https://docs.conda.io/en/latest/miniconda.html

# Estableciendo el entorno virtual

Crear entorno virtual e instalar dependencias (solo la primera vez):

    Linux: make create-env
    Windows (anaconda prompt):
        conda create --name dz3 python=3.8.16
        pip install -r requirements

Activar entorno virtual:

    VSCode (linux) o Anaconda prompt (Windows): conda activate dz3
    
# Ejecutar dashboard:

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


