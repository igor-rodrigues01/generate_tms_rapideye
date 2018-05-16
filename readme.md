# Script para Geração de TMS de Imagens Rapideye

<br/>
## Pré Requisitos de Sistema
- Instalar gdal >= 2.x
- Instalar dans-gdal-scripts
- Possuir um ambiente virtual com o python35 como default e python27

-------------

<br/>
## Pré Requisitos do Script
- Instalar as libs contidas em process_re/requirements.txt

```shell
pip install -r requirements.txt
```

-------------
<br/>
## Funcionamento

- Este script tem como objetivo gerar TMS's de imagens rapideye e salva-las em banco.
- Esta ferramenta funciona com todas as suas fucionalidades ao utilizar o arquivo **file_manager.py**
ou funciona de forma isolada com os script **footprint.py** ou **generate_tms.py**.

> #### Nota
> O footprint gerado é baseado em um VRT mascarado, logo, caso a imagem esteja corrompida isso será ignorado e o footprint será gerado normalmente.
>

<br/>

### Funcionamento do script completo (utilizando file_manage.py):
>##### Com este script é possível:
> - *Processar um lote de imagens baseado na constante FILE_ALL_RAPIDEYE* (movendo para outro diretório ou não)
> - *Processar apenas uma imagem passada como argumento de linha de comando* (movendo para outro diretório ou não)
> 

- Reorganização e recomposição de bandas para 3 5 2 ao lado do .tif (definição das bandas estão em constans.py)
- Geração de TMS's
- Aplicação de constraste streach
- Geração de footprint para obtenção de geometria para inserção em banco
- Geração de PNG (quicklook)
- Obtenção do path da imagem (baseado em contants.py) 
- Obtenção do path do RGB 
- Obtenção do path do PNG 
- Obtenção do path do xml do tms 
- Obtenção do percentual de nuvens
- Inserção destas informações em banco
- geração de logs de sucesso e erro para cada processamento
- Será movido as imagens do path de origem para um path de destino (definidos em constants.py).
    - o path default de origem é "/csr/imagens/rapideye/4a_cobertura"
    - o path default de destino é "/csr/imagens/rapideye"

#### Formas de uso:
- Processameto baseado em um lote de imagens definido na constante *FILE_ALL_RAPIDEYE*
```shell
python file_manager.py -dirImgs /path/to/rapideye/4a_cobertura/
```

- Processameto baseado em um lote de imagens definido na constante *FILE_ALL_RAPIDEYE* e movendo para outro diretório (o destino está definido na constante DESTINY_RAPIDEYE)
```shell
python file_manager.py -dirImgs /path/to/rapideye/4a_cobertura/ -move 1
```

- Processameto apenas uma imagem
```shell
python file_manager.py -dirImgs /path/to/dir_img/ -oneImg 1
```

- Processameto apenas uma imagem e movendo para outro diretório (o destino está definido na constante DESTINY_RAPIDEYE) 
```shell
python file_manager.py -dirImgs /path/to/dir_img/ -oneImg 1 -move 1
```
-----------------
<br/>

### Funcionamento do script *footprint.py*
>##### Com este script é possível:
> - *Gerar o footprint do tif em um shapefile.*
> - *Gerar um footprint em um shapefile e exportar a geometria em um arquivo WKT.*

- Poligonizar e reprojetar um tif rapideye
- Caso necessário, solicitar exportação de geometria gerada como wkt 

#### Formas de uso:
- Geração de shapefile
```shell
python footprint.py -imgIn /path/to/img.tif -footOut /path/to/result/my_foot
```
- Geração de shapefile com exportação de wkt
```shell
python footprint.py -imgIn /path/to/img.tif -footOut /path/to/result/my_foot -wkt 1
```
-----------------
<br/>

### Funcionionamento do script *generate_tms.py*
>##### Com este script é possível:
> - *Gerar o TMS de um imagem rapideye*

- Reorganização e recomposição de bandas para 3 5 2 ao lado do .tif (a definição das bandas está em constans.py)
- Aplicação de constraste streach
- Geração de TMS's

#### Forma de uso:

```shell
python generate_tms.py -imgPathIn /path/to/img.tif -br 3 -bg 5 -bb 2 -rgbPathOut /path/to/dir_rgb -zoomMin 2 -zoomMax 5 -link http://127.0.0.1/imgs -dirTms /path/to/dir_tms
```
