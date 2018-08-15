#!/bin/bash
export GOOGLE_APPLICATION_CREDENTIALS=~/gcloud/apikey.json
rm ../output/*ServiceOutput* 2>/dev/null
rm ../output/*EOBentries* 2>/dev/null
rm ../output/*temp*.jpg
rm ../output/*doc*.pdf
#If a pdf, first convert pdf to images of each page
if [[ $1 == *.pdf ]]
then
#    rm temp* 2>/dev/null
    echo "Converting PDF into image format"
    python separatepdfs.py $1
    if [[ $? == 1 ]]
    then
        echo "Unsuccesful Conversion"
    else
        COUNT=$(ls -lR ./${1::-4}temp*.jpg | wc -l)
        #For each page, conduct ocr using the ocrdoctest5.py script
        for ((i=0;i<COUNT;i++));
        do
#            echo "Enhancing Image"
#            python modimage.py ${1::-4}temp$i.jpg
            #For the first page, do ocr without knowing the type of document. For other pages, conduct ocr with knowledge of the type
            if [[ $i == 0 ]]
            then
                echo "Conducting ocr on page 1"
                python ocrdoctest5.py ${1::-4}temp$i.jpg #2>/dev/null
                mapfile -t lines <../output/whatkind.txt
            else
                echo "Conducting ocr on page $((i + 1))"
                if [[ ${lines[0]} = *"BILL"* ]]
                then
                    python ocrdoctest5.py ${1::-4}temp$i.jpg -b #2>/dev/null
                elif [[ ${lines[0]} = *"EOB"* ]]
                then
                    python ocrdoctest5.py ${1::-4}temp$i.jpg -e #2>/dev/null
                elif [[ ${lines[0]} = *"OTHER"* ]]
                then
                    python ocrdoctest5.py ${1::-4}temp$i.jpg -o #2>/dev/null
                else
                    python ocrdoctest5.py ${1::-4}temp$i.jpg #2>/dev/null
                fi
            fi
        done
        if [[ $? == 1 ]]
        then
            echo "OCR was unsucessful"
        else
            #Combinedocs.py is run to generate ServiceOutputFinal.txt
            echo "Aggregating results on service"
            python combinedocs.py $1 2>/dev/null
            if [[ $? == 1 ]]
            then
                echo "Could not aggregate results. See ServiceOutputn for more info"
            else
                echo "Process Complete"
            fi
        fi
    fi
#For single page images, run the following
elif [[ $1 == *.jpg ]] || [[ $1 == *.gif ]] || [[ $1 == *.png ]]
then
#    echo "Enhancing Image"
#    python modimage.py $1
    echo "Conducting ocr on image"
    python ocrdoctest5.py $1 #2>/dev/null
    if [[ $? == 1 ]]
    then
        echo "OCR was unsuccesful"
    else
        echo "Aggregating results on service"
        python combinedocs.py $1 #2>/dev/null
        if [[ $? == 1 ]]
        then
            echo "Could not aggregate results. See ServiceOutput0.txt for more info"
        else
            echo "Process Completed"
        fi
    fi
else
    echo "Unsupported file type"
fi

#Cleanup the NLP documents
python cleanupfile.py ../output/NLPHORIZONTALS.txt 2>/dev/null
python cleanupfile.py ../output/NLPSERVICELINES.txt 2>/dev/null

#Here, create a folder for the date of service, if it doesnt exist and move the file we were analyzing, as well as ServiceOutputFinal to the directory. If it does exist,
#ie. there are other documents for the same date of service, add the file and its corresponding output to the directory 
mapfile -t liness <${1::-4}ServiceOutputFinal.txt
if [ -d ../output/${liness[1]:6} ]
then
    echo ""
else
    mkdir ../output/${liness[1]:6}
fi

if [ -d ../output/${liness[1]:6} ]
then
    mv ${1::-4}ServiceOutputFinal.txt  ../output/${liness[1]:6}/
    mv $1 ../output/${liness[1]:6}
    mv ${1::-4}* ../output/${liness[1]:6}
fi
