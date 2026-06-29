# Grid-Navigation Game Experiment

This section documents an experiment that uses a grid‑navigation game to measure how LLM precision degrades over long decision horizons.

`power_model_tester.py`: this is the python source code used to run Experiments 1, 2, 3 and 5 for evaluation models except anthropic models.

`power_model_tester_anthropic.py`: this is the python source code used to run Experiments 1, 2, 3 and 5 for anthropic models.

`power_model_precision_tester.py`: this is the python source code used to run Experiment 4 for evaluation models except anthropic models.

`power_model_precision_tester_anthropic.py`: this is the python source code used to run Experiments 4 for anthropic models.

`config_exp1_exp4.json`: JSON configuration file specifying the model name and other settings for Experiment 1, used by `power_model_tester.py` and `power_model_tester_anthropic.py`. It is also used by `power_model_precision_tester.py` and `power_model_precision_tester_anthropic.py` for Experiment 4.

`config_exp2.json`: JSON configuration file specifying the model name and other settings for experiment 2 used by `power_model_tester.py` and `power_model_tester_anthropic.py`.

`config_exp3.json`: JSON configuration file specifying the model name and other settings for experiment 3 used by `power_model_tester.py` and `power_model_tester_anthropic.py`.

`config_exp5.json`: JSON configuration file specifying the model name and other settings for experiment 5 used by `power_model_tester.py` and `power_model_tester_anthropic.py`

`results`: this folder contains the results generated for each evaluated model.

`test-cases`: this folders contains different test cases used in the experiment.

`exp_documentation`: this markdown file contains the documentation of the experiment including: purpose, approach, results and conclusion.
