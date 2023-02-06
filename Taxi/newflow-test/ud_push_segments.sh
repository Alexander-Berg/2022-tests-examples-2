claims=$1

if [[ $claims == "" ]]
then
	claims=5
fi

echo push $claims claims

python3 client.py -p +70009993344 --batch-client --claims $claims --taxi-class courier --request requests/batch.json --randomize-dropoff-coordinates --randomize-pickup-coordinates
