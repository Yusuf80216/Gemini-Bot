echo "BUILD START"
pip install -r requirements.txt
python manage.py collectstatic --noinput --clear
echo "BUILD END"