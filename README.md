El dashboard fue desarrollado en Windows, pero luego fue migrado refactorizado en Linux.
En este S.O., los comandos como *make* y *git* son instalados fácilmente desde
su terminal mediante el comando <sudo apt install ...>.
Además, dado que su terminal ya incluye Bash, la terminal de VSCode por defecto,
también trabaja con Bash.

------------------------------------------------------------------------------

## Instrucciones para Windows:

Instalar Git:
	
    https://git-scm.com/download/win

En la terminal de VSCode:

Ejecutar el siguiente comando para ingresar correo asociado a Github:

```bash
git config --global user.email "user@email.com"
```

Ingresar a la carpeta donde se quiera guardar el repositorio y clonar desde Github:
	
```bash
git clone https://github.com/rosepb28/Dashboard.git
```

Seleccionar terminal de Bash:

    F1 > Terminal: Select Default Profile > Git Bash
------------------------------------------------------------------------------

## Instalar anaconda o miniconda

Buscar versión 3.8 de Python

    https://docs.conda.io/en/latest/miniconda.html

## Estableciendo el entorno virtual

Crear entorno virtual e instalar dependencias (solo la primera vez):

    Linux: make create-env
    
    Windows (anaconda prompt): conda create --name dz3 python=3.8.10
                               pip install -r requirements.txt

En VSCode:

    Press F1 > Python: Select Interpreter > Python 3.8.10 ('dz3')

Ejecutar comando:

En caso la opción anterior no haga efecto en Windows, abrir el Anaconda Prompt:
```bash
conda activate dz3
```
Luego ingresar al directorio raíz del proyecto.
    
## Opciones para ejecutar dashboard:

Desde directorio raíz (Dashboard/):

Generar SOLO dashboard: 

```bash
python app.py
```

Generar dashboard y reporte diario: 

```bash
python app.py --daily
```

Generar dashboard y reporte mensual: 

```bash
python app.py --monthly
```

Generar dashboard, reporte diario y mensual: 

```bash
python app.py --daily --monthly
```
Generar reporte diario y mensual, o escoger el que se requiera: 

```bash
python reports.py --daily --monthly
```

**Opcional**: Guardar la página en un archivo *url.html* y se quiere leer los datos desde ahí cambiando valor de *url_from_file* en [config.yaml](config.yaml), a *True*.
Usar un archivo ya guardado en lugar de leer la web cada vez que se genere el dashboard, siempre tomará menos tiempo.

## Comandos para actualizar archivos en la carpeta Data/Series:

**SIEMPRE** ejecutar los siguientes comandos para actualizar el repositorio:

```bash
git fetch
git pull
```

Para cargar los datos actualizados durante la semana (generalmente los viernes):

```bash
git add .
git commit -m "Escribir comentario aquí."
git push
```