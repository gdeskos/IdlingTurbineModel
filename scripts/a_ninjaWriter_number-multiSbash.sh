!#/bin/bash


fileNum=1

ninjaString="aa_ninjaFiles"
serialBash="a_serial.sh"

if [ ! -d "$ninjaString" ]; then
    mkdir -p "$ninjaString"
fi

ii=0

rm -rf $ninjaString*
rm -rf $serialBash

echo "!#/bin/bash" >> $serialBash


for file in $(find -wholename "./unsteady/*.fst"); do

    if [[ $(( 10#$ii % 102 )) == 0 ]]
    then
        echo writing ${ii}: file $i in $fileNum
        echo " " >> $NinjaFile

        # echo writing $i in $fileNum
        NinjaFile="${ninjaString}/build-batch_${fileNum}.ninja"
        echo rule run_openfast > $NinjaFile
        echo "  command = /projects/bar/mchetan/tools/openfast/tightCoupling-mc-FullUA/build/glue-codes/openfast/openfast \$in > \$out 2>&1" >> $NinjaFile
        echo " " >> $NinjaFile
        fileNum=$(($fileNum+1))

        echo "sbatch Submit-serial.sh ${NinjaFile}" >> $serialBash
        
    fi

    echo "build ${file}.stdOut: run_openfast ${file}" >> $NinjaFile


    ii=$(($ii+1))

done
