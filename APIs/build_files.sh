echo "BUILD START"
source venv/bin/activate
pip install -r requirements.txt
python manage.py collectstatic --noinput --clear
echo "BUILD END"