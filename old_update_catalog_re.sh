#!/bin/bash
#
#### Functions
#
msg_error(){
  local name_script=$(basename $0)
  echo "Usage: $name_script <footprint_shp> <tileid>" >&2
  echo "<footprint_shp> is a Shapefile for Footprint" >&2
  echo "<tileid> Tile ID of bulk of images" >&2
  exit 1
}
#
set_enviroment_tms(){
  min=2
  max=18
  dir_png="/csr/imagens/png/rapideye"
  dir_tms="/csr/imagens/tms/rapideye"
  url_tms="http://10.1.25.66/imagens/tms/rapideye"
  r=3
  g=5
  b=2
  suffix_rgb="r"$r"g"$g"b"$b
}
#
set_enviroment_pg(){
  PGHOSTADDR="10.1.8.58"
  PGUSER="indicarprocess"
  PGPASSWORD="ind!c@rprcss"
  PGDATABASE="siscom"
  table_catalog=ibama.img_catalogo_rapideye_a
  export PGUSER PGPASSWORD PGHOSTADDR PGDATABASE
}
#
reset_enviroment_pg(){
  PGHOSTADDR=""
  PGUSER=""
  PGPASSWORD=""
  PGDATABASE=""
  export PGUSER PGPASSWORD PGHOSTADDR PGDATABASE
}
#
tileid_log(){
  # $1 = Message for log - Can't have SPACE AND '...' in message
  msgtileid=$(echo $msgtileid | sed 's/\.\.\./ /g')
  msgtileid=$msgtileid"-"$1"..."
  local item
  for item in $msgtileid; do echo $item; done > $logtileid
}
#
remove_tileid(){
  # List for TMS
  local sql="SELECT '/csr/imagens/tms/rapideye/' || split_part(tms, '/', 7) as xml FROM "$table_catalog" WHERE split_part(image, '_', 1) = '"$tileid"'"
  local xml_lst=$(psql "-c $sql" | grep '_tms.xml')
  # Catalog
  tileid_log "Remove:Footprint"
  sql="DELETE FROM "$table_catalog" WHERE split_part(image, '_', 1) = '"$tileid"'"
  psql "-c $sql" > /dev/null 2>> $logtileiderror
  # Remove TMS
  local total=$(echo $xml_lst | wc -w)
  local num=1
  local item
  for item in $xml_lst
  do
    tileid_log $num"/"$total")Remove:"$item
    rm -f $item 2>> $logtileiderror
    rm -f -r $(echo $item | sed 's/_tms.xml/.tms/g') 2>> $logtileiderror
    num=$(echo $num"+1" | bc)
  done
}
#
insert_catalog(){
  tileid_log "Insert:Footprint"
  # Export CSV
  if [ -f $csv ]; then
    rm $csv
  fi
  local sql="SELECT path, image, total_part, cloud_per, ST_AsText( ST_Multi( geometry ) ) as wkt FROM $layer_name WHERE tileid = $tileid"
  ogr2ogr -dialect SQLITE -sql "$sql" -f CSV $csv $shp
  # Insert
  ./home/wille/indicar-process/indicarprocess/catalogo/bin/scripts-rapideye/script/csv2sqlinsert.py $csv $suffix_rgb $table_catalog
  sql=$layer_name"_"$tileid".sql"
  psql -f $sql > /dev/null 2>> $logtileiderror
  # Clean
  rm $sql $csv
}
#
rgb_tms(){
  local sql="SELECT path || '/' || image AS source FROM "$layer_name" WHERE tileid = "$tileid
  if [ -f $csv ]; then
    rm $csv
  fi
  ogr2ogr -dialect SQLITE -sql "$sql" -f CSV $csv $shp
  sed -i '1d' $csv
  local total=$(cat $csv | wc -l)
  local num=1
  # Create RGB + TMS
  local item
  for item in $(cat $csv)
  do
    tileid_log $num"/"$total")2_rgb:"$item
    2_rgb.sh $item $r $g $b > /dev/null 2>> $logtileiderror
    tileid_log $num"/"$total")16b_2_8b_convert:"$item
    rgb=$(echo $item | sed 's/.tif/_'$suffix_rgb'.tif/g')
    16b_2_8b_convert.sh $rgb > /dev/null 2>> $logtileiderror
    tileid_log $num"/"$total")mk_tiles.sh:"$item
    mk_tiles.sh $rgb $min $max $dir_png $dir_tms $url_tms > /dev/null 2>> $logtileiderror
    num=$(echo $num"+1" | bc)
  done
  rm $csv
}
####
#
totalargs=2
#
if [ $# -ne $totalargs ] ; then
  msg_error
  exit 1
fi
#
shp=$1
tileid=$2
#
if [ ! -f "$shp" ]; then
  echo "The file '$shp' not exist" >&2
  exit 1
fi
#
layer_name=${shp%.*}
csv=$layer_name"_"$tileid".csv"
log="update_catalog_re.log"
logtileid="update_catalog_re_"$tileid".log"
logtileiderror="update_catalog_re_"$tileid"_error.log"
msgtileid=""
#
set_enviroment_tms
set_enviroment_pg
#
echo $tileid >> $log
remove_tileid
rgb_tms
insert_catalog
#
reset_enviroment_pg
#

if [ -f "$logtileiderror" ]; then
  if [ $(cat $logtileiderror | wc -w) -eq 0 ]; then
    rm $logtileiderror
  fi
fi
rm $logtileid
