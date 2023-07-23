
``` dev setup (Windows)
pip install poetry
poetry config virtualenvs.in-project true
poetry env use python
poetry install
poetry shell
copy .\.env.example .env 
# add sender email and password to .env file 
uvicorn test_v_email:app --reload

```
