# Script para Geração de TMS de Imagens Rapideye

## Sumário
- [Objetivo](#objetivo)
- [Pré requisitos de sistema](#pre-requisitos-do-sistema)
- [Pré requisitos do script](#pre-requisitos-do-script)
- [Funionamento do script completo](#foo)
- [Funcionamento do script *footprint.py*](#foo)
- [Funcionionamento do script generate_tms.py](###Funcionionamento do script generate_tms.py)
- [Arquivo de configurações](#arquivo-de-configuracoes)
- [Passo a passo do script completo](#passo-a-passo-do-script-completo)
- [Modelo de atributos em banco](#foo)

<br/>
<br/>
## Objetivo

- Este script tem como objetivo gerar TMS's de imagens rapideye e salva-las em banco.
- Esta ferramenta funciona com todas as suas fucionalidades ao utilizar o arquivo **file_manager.py**.
Se preferir utilizar suas funcionalidades de forma isolada, basta utilizar os scripts **footprint.py** e/ou **generate_tms.py**.

> #### Nota
> O footprint gerado é baseado em um VRT mascarado, logo, caso a imagem esteja corrompida, isso será ignorado e o footprint será gerado normalmente.
>

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
> #### Nota
>- Este ambiente virtual deve possuir a lib gdal disponível para o python35 e python 27

-------------
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

- Processameto de apenas uma imagem
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

## Arquivo de configurações
> **DESTINY_RAPIDEYE** - Diretório de destino para onde as imagens serã movidas **<'/home/user/'>**
<br/>
> **TOTAL_PART** - Valor estático para precher o campo *total_part* da tabela. Este valor é estático pois, a geração de footprint será baseado em um .vrt mascarado, logo, qualquer falha nos pixels da imagem será ignorado e a poligonização será gerada normalmente. **<1>**
<br/>
> **FILE_ALL_RAPIDEYE** - Path de arquivo com todas as imagens a serem processada. É aconselhado que seja passa apenas um arquivo com um lote de imagens por vez. **<"/home/user/lotes/lote_1.txt">**
<br/>
> **OUTSIZE_RGB** - Percentual da resolução de saída da imagem  <**10**>
<br/>
> **B52_PATH** = Path para o ponto de montagem do b52 <**\\\\10.1.25.66\\b52_imagens\\rapideye\\**>
<br/>
> **DIR_PNG** - Path do diretório que serão gerados os PNG's. **<"/home/user/png">**
<br/>
> **DIR_PNG_TO_DB** - Path do png que será inserido em banco (é útil para pontos de montagens). **<<span>http:<span>//10.1.25.x/imagens/png/>**
<br/>
> **DIR_TMS** = Path do diretório que serão gerados os TMS's. **<"/home/user/tms">**
<br/>
> **URL_TMS** = "http://10.1.8.69/TMS-TESTE"
<br/>
> **ZOOM_MIN** = Valor mínimo de zoom para o TMS <**2**>
<br/>
> **ZOOM_MAX** = Valor máximo de zoom para o TMS <**10**>
<br/>
> **BAND_R** = Banda Red <**3**>
<br/>
> **BAND_G** = Banda Green <**5**>
<br/>
> **BAND_B** = Banda Blue <**2**>
<br/>
<br/>
> Dados de Conexão com Banco
<br/>
<br/>
> **HOSTADDR** = Ip do servidor da base de dados <**10.1.8.X**>
<br/>
> **USER** = Usuário para acesso a base de dados <**postgres**>
<br/>
> **PASSWORD** = Senha para acesso a base de dados <**123456**>
<br/>
> **DATABASE** = Nome da base de dados <**my_siscom**>
<br/>
> **SCHEMA** = Schema para a tabela <**ibama**>
<br/>
> **TABLENAME_RAPIDEYE_CATALOG** = Tabela de imagens rapideye <**img_catalogo_rapideye_a**>
