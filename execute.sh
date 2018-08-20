#!/bin/bash
export GOOGLE_APPLICATION_CREDENTIALS=~/gcloud/apikey.json

python prefix.py $1
mapfile -t filenames <dirname.txt

rm ${filenames[1]}
rm ${filenames[2]}
rm ${filenames[3]}
rm ${filenames[4]}

#If a pdf, first convert pdf to images of each page
if [[ $1 == *.pdf ]]
then
#    rm temp* 2>/dev/null
    echo "Converting PDF into image format"
    python separatepdfs.py $1
    if [[ $? == 1 ]]
    then
        echo "Unsuccessful Conversion"
        exit 0
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
                mapfile -t lines <${filenames[5]}
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
            echo "OCR was unsuccessful"
            exit 0
        else
            #Combinedocs.py is run to generate ServiceOutputFinal.txt
            echo "Aggregating results on service"
            python combinedocs.py $1 2>/dev/null
            if [[ $? == 1 ]]
            then
                echo "Could not aggregate results. See ServiceOutputn for more info"
                exit 0
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
        echo "OCR was unsuccessful"
        exit 0
    else
        echo "Aggregating results on service"
        python combinedocs.py $1 #2>/dev/null
        if [[ $? == 1 ]]
        then
            echo "Could not aggregate results. See ServiceOutput0.txt for more info"
            exit 0
        else
            echo "Process Completed"
        fi
    fi
else
    echo "Unsupported file type"
fi

#Cleanup the NLP documents
python cleanupfile.py ${filenames[7]} 2>/dev/null
python cleanupfile.py ${filenames[6]} 2>/dev/null

#Here, create a folder for the date of service, if it doesnt exist and move the file we were analyzing, as well as ServiceOutputFinal to the directory. If it does exist,
#ie. there are other documents for the same date of service, add the file and its corresponding output to the directory 
mapfile -t liness <${1::-4}ServiceOutputFinal.txt
#if [ -d ${filenames[0]}${liness[1]:6} ]
#then
#    echo ""
#else
#    mkdir ${filenames[0]}${liness[1]:6}
#fi

#if [ -d ${filenames[0]}${liness[1]:6} ]
#then
#    mv ${1::-4}ServiceOutputFinal.txt  ${filenames[0]}${liness[1]:6}/
#    mv $1 ${filenames[0]}${liness[1]:6}
#    mv ${1::-4}* ${filenames[0]}${liness[1]:6}
#fi

#Move all intermediary files to temp folder
empty=""
if [ -d ${filenames[0]}inter ]
then
    echo ""
else
    mkdir ${filenames[0]}inter
fi

if [ -f ${filenames[0]}inter/${1/${filenames[0]}/$empty::-4}ServiceOutput0.txt ]
then
    rm ${filenames[0]}inter/${1/${filenames[0]}/$empty}*
fi

if [ -d ${filenames[0]}inter ]
then
    mv ${1::-4}* ${filenames[0]}inter
    mv ${filenames[0]}inter/*ServiceOutputFinal.txt ${filenames[0]}
    mv ${filenames[0]}inter/${1/${filenames[0]}/$empty} ${filenames[0]}
fi
