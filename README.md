# Thesis Repository
> LLM training for translating natural language into structured queries and executing them in a graph database

Thesis text will be available soon!

## Folders
- `data`: This is where the results, generated questions and schema JSONs are stored
- `db_dumps`: Dump files of the 3 Neo4J Databases
- `project`: The Python project code
- `scripts`: Various Python scripts

## How to run the project
1) Run `pip install -r requirements.txt`
2) Define the following envs:
    - `BENCH_MAX_THREADS`: The number of threads to use for the benchmark
    - `FEATHERLESS_TOKEN`: Your Featherless AI token
    - `NEO_FTTH_URI`, `NEO_FTTH_USER`, `NEO_FTTH_PASS`: Neo4J server credentials for the FTTH Dataset
    - `NEO_HOSPITAL_URI`, `NEO_HOSPITAL_USER`, `NEO_HOSPITAL_PASS`: Neo4J server credentials for the Hospital Dataset
    - `NEO_ECOMM_URI`, `NEO_ECOMM_USER`, `NEO_ECOMM_PASS`: Neo4J server credentials for the Ecommerce Dataset
3) Run `python main.py`

## Datasets
All 3 datasets are available as dump files [here](./db_dumps)

Dataset Sources:
- **FTTH Dataset**: generated using the [generate_ftth_dataset.py](./scripts/generate_ftth_dataset.py) script
- **Hospital Dataset**: converted from [this](https://www.kaggle.com/datasets/mshamoonbutt/hospital-management-system) dataset using Neo4J Aura's AI schema import
- **Ecommerce Dataset**: converted from [this](https://www.kaggle.com/datasets/parsakh/global-e-commerce-and-supply-chain-database) dataset using Neo4J Aura's AI schema import

## License

MIT License

```
Copyright (c) 2026 Nikolas Spiridakis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
