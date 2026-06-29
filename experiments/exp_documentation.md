# Documentation of Grid-Navigation Game Experiment

## 1. Experiment 1: Precision Degradation Over Long Horizons

### 1.1 Purpose

The purpose of this experiment is to isolate and measure execution precision degradation in LLMs over long sequential horizons. By framing the task as a simple, fully deterministic game with a fixed and minimal output space, the experiment removes confounding factors such as open‑ended generation, ambiguity, stochastic reasoning, and complex problem‑solving.

This design allows errors to be attributed unambiguously to failures in state tracking, rule application, or step‑by‑step execution consistency as sequence length increases. The experiment is not intended to test reasoning capability or intelligence, but rather to evaluate whether LLMs can reliably and repeatedly apply straightforward rules over extended sequences without drifting, accumulating errors, or losing positional accuracy.

### 1.2 Approach

#### 1.2.1 Treasure Hunt Grid Game Design

The experimental task is Treasure Hunt, a deterministic grid‑navigation game played on a fixed 10×10 board. Before each test, the board is randomly initialized with 20 trap squares and 10 gold squares; the remaining 70 squares are empty. The complete board configuration is provided to the model upfront, before any moves are executed.

All movement rules are deterministic. A move to the right increments the X coordinate by 1; left decrements X by 1; up increments Y by 1; and down decrements Y by 1. Any move that would exit the board boundaries results in a "BLOCKED" response. Landing on a gold square yields "YIPEE", landing on a trap yields "OUCH", and landing on an empty square yields "OK". Once visited, gold and trap squares permanently become empty.

For each test, the model receives the full board layout along with a sequence of *T* moves and is required to act as the game engine itself. It must return a JSON object containing the correct response for every move, as well as cumulative counts of gold collected and traps triggered. The entire move sequence is submitted in a single API call, requiring the model to track board state and apply rules autonomously across the full horizon.

#### 1.2.2 Experimental Evaluation Criteria

**Fixed and minimal output space.**  
At every step, the correct output is one of exactly four possible responses: "OK", "YIPEE", "OUCH", or "BLOCKED". This is not an open‑ended reasoning task but a four‑class, deterministic classification problem. The experiment does not aim to assess problem difficulty, but rather the model’s ability to reliably execute simple rules over increasing sequence length *T*.

**Token usage does not scale meaningfully with sequence length.**  
As *T* increases, prompt size grows only modestly. The board description remains constant, and move sequences are short strings. This experiment does not test context window limits or memory exhaustion. Measurements confirm that even at NS = 300, prompt token counts remain well within model limits. Any observed degradation is therefore attributable to declining execution precision over long horizons, not context overflow.

**Perfect accuracy is theoretically achievable.**  
A straightforward Python implementation performs this task with 100% accuracy for arbitrary *T*. Given the board layout and prior moves, the correct response at each step is uniquely determined. There is no randomness, ambiguity, or alternative valid output.

**Binary task completion as the primary metric.**  
The primary evaluation metric is whether a test sequence is completed without any errors—a binary outcome. This reflects practical autonomous‑agent requirements: a trajectory that is mostly correct but contains a single error may be functionally useless. Partial correctness is therefore insufficient for success under the measured objective.

#### 1.2.3 Test Configuration

| Parameter | Value |
|-----------|-------|
| Boards per test set (NT) | 20 |
| Games per board (NG) | 1 |
| Sequence lengths tested (NS) | 2, 5, 10, 20, 50, 100, 200, 300 moves |
| Board size | 10 × 10 grid |
| Gold squares per board | 10 |
| Trap squares per board | 20 |
| Possible responses per move | 4 (OK, YIPEE, OUCH, BLOCKED) |
| API temperature | 1 |
| Call structure | Single API call per test (full board + all moves in one prompt) |
| Scoring | Per-move comparison against pre-computed ground truth |
| Primary metric | Proportion of tests completed with zero errors (binary) |
| Inclusion threshold | At least one perfect game at any sequence length |
| Token regime | Prompt tokens constant per NS; no context window exhaustion observed |

### 1.3 Results Table

The table below presents the primary metric: proportion of 20 tests completed without any error, for each model at each sequence length. This is the “perfect test” binary measure.

| Model | NS=2 | NS=5 | NS=10 | NS=20 | NS=50 | NS=100 | NS=200 | NS=300 |
|-------|------|------|-------|-------|-------|--------|--------|--------|
| gpt-5.3-chat-latest | 100% | 100% | 100% | 100% | 100% | 85% | 25% | 0% |
| Kimi-K2.5 | 100% | 100% | 100% | 100% | 95% | 85% | Time out | Time out |
| o4-mini | 100% | 100% | 100% | 95% | 95% | 80% | 5% | 0% |
| gpt-5.2-chat-latest | 100% | 100% | 100% | 100% | 100% | 70% | 0% | 0% |
| o3-mini | 100% | 100% | 100% | 95% | 85% | 75% | 5% | 10% |
| model-router | 100% | 100% | 100% | 100% | 85% | 45% | 5% | 5% |
| grok-4-fast-reasoning | 100% | 100% | 100% | 90% | 100% | 20% | 5% | 0% |
| DeepSeek-R1 | 100% | 100% | 100% | 90% | 80% | 10% | 5% | 0% |
| DeepSeek-R1-0528 | 100% | 100% | 100% | 100% | 50% | 5% | 0% | 0% |
| grok-3-mini | 100% | 100% | 100% | 95% | 90% | Time out | Time out | Time out |
| grok-4-1-fast-reasoning | 100% | 100% | 95% | 90% | 85% | 0% | 0% | 0% |
| gpt-5.1-chat-latest | 100% | 100% | 95% | 90% | 0% | 0% | 0% | 0% |
| claude-opus-4-5 | 100% | 100% | 90% | 95% | 0% | 0% | 0% | 0% |
| claude-opus-4-6 | 100% | 90% | 90% | 95% | 0% | 0% | 0% | 0% |
| claude-sonnet-4-5 | 95% | 80% | 95% | 85% | 0% | 0% | 0% | 0% |
| claude-opus-4-1 | 100% | 80% | 80% | 70% | 0% | 0% | 0% | 0% |
| grok-3 | 95% | 90% | 90% | 55% | 15% | 0% | 0% | Time out |
| gpt-5.4-mini | 100% | 65% | 60% | 10% | 0% | 0% | 0% | 0% |
| gpt-5-chat-latest | 70% | 60% | 50% | 15% | 0% | 0% | 0% | 0% |
| gpt-5.4-nano | 70% | 50% | 50% | 15% | 0% | 0% | 0% | 0% |
| gpt-4o | 95% | 60% | 40% | 5% | 0% | 0% | 0% | 0% |
| DeepSeek-V3.1 | 95% | 55% | 35% | 5% | 0% | 0% | 0% | 0% |
| DeepSeek-V3.2 | 90% | 55% | 30% | 15% | 0% | 0% | Time out | Time out |
| Mistral-Large-3 | 90% | 20% | 25% | 10% | 0% | 0% | 0% | 0% |
| claude-haiku-4-5 | 75% | 65% | 45% | 0% | 0% | 0% | 0% | 0% |
| Llama-4-Maverick-17B-128E-Instruct-FP8 | 75% | 40% | 15% | 0% | 0% | 0% | 0% | 0% |
| cohere-command-a | 65% | 25% | 20% | 0% | 0% | 0% | 0% | 0% |
| grok-4-1-fast-non-reasoning | 55% | 20% | 15% | 0% | 0% | 0% | 0% | 0% |
| claude-sonnet-4-6 | 100% | 45% | 0% | 0% | 0% | 0% | 0% | 0% |

### 1.4 Conclusion

This experiment demonstrates:

- All models fail to maintain perfect precision indefinitely. The task is trivially solvable by algorithm; the LLMs are not.

- Collapse is rapid and near-total once the threshold is crossed. The average failures per failed game metric reveals that once a model’s internal state diverges, it rarely recovers. Error cascades for the remainder of the sequence.

- Architectural differences determine the threshold, not just scale. Models with reasoning control mechanisms (CoT state, RL reasoning, live routing signal) sustain precision longer. Models without these mechanisms show high per-step error rates.

- This is not a token or memory problem. Prompt token counts confirm that context exhaustion is not the mechanism. The degradation is in reasoning precision over sequential steps.

- Scaling is real and beneficial, but insufficient.

## 2. Experiment 2: Impact of Incremental Rule Complexity on LLM Precision

### 2.1 Purpose

The goal is to determine whether adding a small amount of complexity—specifically, one additional rule—has a significant impact on the results. The question is whether LLMs can absorb the marginal increase in per-step complexity without measurable degradation.

### 2.2 Approach

The approach remains the same as before, with the addition of a simple rule to the game: if the current move is "OK" and the previous move was also "OK", then return "MOVING".
With this rule included, there are now five possible responses: "OK", "YIPEE", "OUCH", "MOVING", and "BLOCKED". The model must track the previous step’s result to determine the current output.

This modification does not increase the board complexity, the number of moves, the prompt length, or the difficulty of any individual classification decision. It adds only a single conditional check on the immediately preceding output.

### 2.3 Results Table

The table below presents the primary metric: proportion of 20 tests completed without any error, for each model at each sequence length. This is the “perfect test” binary measure.

| Model | NS=2 | NS=5 | NS=10 | NS=20 | NS=50 | NS=100 | NS=200 | NS=300 |
|-------|------|------|-------|-------|-------|--------|--------|--------|
| gpt-5.3-chat-latest | 100% | 100% | 100% | 100% | 100% | 100% | 15% | 0% |
| Kimi-K2.5 | 100% | 100% | 100% | 85% | 75% | 65% | 25% | 10% |
| o4-mini | 100% | 100% | 95% | 95% | 80% | 65% | 5% | 0% |
| gpt-5.2-chat-latest | 100% | 100% | 100% | 100% | 90% | 40% | 0% | 0% |
| o3-mini | 95% | 95% | 90% | 95% | 60% | 30% | 5% | 0% |
| model-router | 100% | 100% | 90% | 95% | 50% | 25% | 0% | 0% |
| grok-4-fast-reasoning | 100% | 100% | 100% | 95% | 55% | 10% | 0% | 0% |
| DeepSeek-R1 | 90% | 80% | 85% | 80% | 40% | 5% | 0% | 0% |
| DeepSeek-R1-0528 | 85% | 80% | 90% | 80% | 20% | 0% | 0% | 0% |
| grok-3-mini | 100% | 100% | 95% | 80% | 75% | Time out | Time out | Time out |
| grok-4-1-fast-reasoning | Time out | Time out | Time out | Time out | Time out | Time out | Time out | Time out |
| gpt-5.1-chat-latest | 100% | 100% | 90% | 80% | 5% | 0% | 0% | 0% |
| claude-opus-4-5 | 100% | 100% | 90% | 85% | 0% | 0% | 0% | 0% |
| claude-opus-4-6 | 100% | 100% | 80% | 45% | 0% | 0% | 0% | 0% |
| claude-sonnet-4-5 | 50% | 15% | 5% | 0% | 0% | 0% | 0% | 0% |
| claude-opus-4-1 | 85% | 75% | 70% | 20% | 0% | 0% | 0% | 0% |
| grok-3 | 50% | 10% | 5% | 0% | 0% | 0% | 0% | 0% |
| gpt-5.4-mini | 50% | 10% | 5% | 0% | 0% | 0% | 0% | 0% |
| gpt-5-chat-latest | 50% | 15% | 0% | 0% | 0% | 0% | 0% | 0% |
| gpt-5.4-nano | 20% | 5% | 0% | 0% | 0% | 0% | 0% | 0% |
| gpt-4o | 35% | 5% | 0% | 0% | 0% | 0% | 0% | 0% |
| DeepSeek-V3.1 | 55% | 15% | 0% | 0% | 0% | 0% | 0% | 0% |
| DeepSeek-V3.2 | 35% | 15% | 0% | 0% | 0% | 0% | 0% | 0% |
| Mistral-Large-3 | 35% | 15% | 0% | 0% | 0% | 0% | 0% | 0% |
| claude-haiku-4-5 | 50% | 10% | 0% | 0% | 0% | 0% | 0% | 0% |
| Llama-4-Maverick-17B-128E-Instruct-FP8 | 40% | 10% | 0% | 0% | 0% | 0% | 0% | Time out|
| cohere-command-a | 10% | 5% | 0% | 0% | 0% | 0% | 0% | 0% |
| grok-4-1-fast-non-reasoning | 25% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |
| claude-sonnet-4-6 | 60% | 5% | 0% | 0% | 0% | 0% | 0% | 0% |

### 2.4 Analysis

#### 2.4.1 Aggregate Impact Summary

The table below presents the average completion rates across all models for each sequence length, comparing the original experiment (experiment 1) against the MOVING rule variant (experiment 2).

| Sequence Length | Original Avg | MOVING Avg | Change    | Models Declined | Models Improved |
|-----------------|--------------|------------|-----------|-----------------|-----------------|
| NS=2            | 92.1%        | 68.6%      | -23.5pp   | 18              | 0               |
| NS=5            | 75.9%        | 52.3%      | -23.6pp   | 18              | 1               |
| NS=10           | 69.7%        | 46.1%      | -23.6pp   | 22              | 0               |
| NS=20           | 55.9%        | 40.5%      | -15.4pp   | 18              | 1               |
| NS=50           | 33.8%        | 23.2%      | -10.6pp   | 10              | 1               |
| NS=100          | 17.0%        | 12.6%      | -4.4pp    | 8               | 1               |
| NS=200          | 1.9%         | 1.9%       | 0.0pp     | 4               | 0               |
| NS=300          | 0.6%         | 0.4%       | -0.2pp    | 2               | 0               |

The MOVING rule’s impact is most severe at short sequence lengths (NS=2 through NS=10), where 18–22 of 29 models showed measurable declines. This is significant: the rule change affects the very first steps of the game, not just long-horizon performance. At NS=2, not a single model improved, while 18 declined. The average completion rate fell from 92.1% to 68.6%, a drop of 23.5 percentage points from a one-rule addition.
At longer sequences (NS=200 and NS=300), the impact appears minimal, but this is an artefact of floor effects: most models were already at 0% and could not decline further. The real story is told in the NS=2 to NS=100 range, where the additional complexity accelerated collapse across nearly every model.

#### 2.4.2 Model-by-Model Performance Delta

The table below reports the change in completion rate (measured in percentage points) for each model across sequence lengths. Negative values indicate that performance under the MOVING rule variant was worse than in the original experiment.

| Model                              | NS=2 | NS=5 | NS=10 | NS=20 | NS=50 | NS=100 | NS=200 | NS=300 |
|------------------------------------|------|------|-------|-------|-------|--------|--------|--------|
| gpt-5.3-chat-latest                | 0    | 0    | 0     | 0     | 0     | +15    | -10    | 0      |
| Kimi-K2.5                          | 0    | 0    | 0     | -15   | -20   | -20    | ---    | ---    |
| o4-mini                            | 0    | 0    | -5    | 0     | -15   | -15    | 0      | 0      |
| gpt-5.2-chat-latest                | 0    | 0    | 0     | 0     | -10   | -30    | 0      | 0      |
| o3-mini                            | -5   | -5   | -10   | 0     | -25   | -45    | 0      | -10    |
| model-router                       | 0    | 0    | -10   | -5    | -35   | -20    | -5     | -5     |
| grok-4-fast-reasoning              | 0    | 0    | 0     | +5    | -45   | -10    | -5     | 0      |
| DeepSeek-R1                        | -10  | -20  | -15   | -10   | -40   | -5     | -5     | 0      |
| DeepSeek-R1-0528                   | -15  | -20  | -10   | -20   | -30   | -5     | 0      | 0      |
| grok-3-mini                        | 0    | 0    | -5    | -15   | -15   | ---    | ---    | ---    |
| grok-4-1-fast-reasoning            | ---  | ---  | ---   | ---   | ---   | ---    | ---    | ---    |
| gpt-5.1-chat-latest                | 0    | 0    | -5    | -10   | +5    | 0      | 0      | 0      |
| claude-opus-4-5                    | 0    | 0    | 0     | -10   | 0     | 0      | 0      | 0      |
| claude-opus-4-6                    | 0    | +10  | -10   | -50   | 0     | 0      | 0      | 0      |
| claude-sonnet-4-5                  | -45  | -65  | -90   | -85   | 0     | 0      | 0      | 0      |
| claude-opus-4-1                    | -15  | -5   | -10   | -50   | 0     | 0      | 0      | 0      |
| grok-3                             | -45  | -80  | -85   | -55   | -15   | 0      | 0      | ---    |
| gpt-5.4-mini                       | -50  | -55  | -55   | -10   | 0     | 0      | 0      | 0      |
| gpt-5-chat-latest                  | -20  | -45  | -50   | -15   | 0     | 0      | 0      | 0      |
| gpt-5.4-nano                       | -50  | -45  | -50   | -15   | 0     | 0      | 0      | 0      |
| gpt-4o                             | -60  | -55  | -40   | -5    | 0     | 0      | 0      | 0      |
| DeepSeek-V3.1                      | -40  | -40  | -35   | -5    | 0     | 0      | 0      | 0      |
| DeepSeek-V3.2                      | -55  | -40  | -30   | -15   | 0     | 0      | ---    | ---    |
| Mistral-Large-3                    | -55  | -5   | -25   | -10   | 0     | 0      | 0      | 0      |
| claude-haiku-4-5                   | -25  | -55  | -45   | 0     | 0     | 0      | 0      | 0      |
| Llama-4-Maverick-17B-128E          | -35  | -30  | -15   | 0     | 0     | 0      | 0      | ---    |
| cohere-command-a                   | -55  | -20  | -20   | 0     | 0     | 0      | 0      | 0      |
| grok-4-1-fast-non-reasoning        | -30  | -20  | -15   | 0     | 0     | 0      | 0      | 0      |
| claude-sonnet-4-6                  | -40  | -40  | 0     | 0     | 0     | 0      | 0      | 0      |

The table below highlights models with the most significant changes, grouped by their performance tier in the original experiment.

| Model                     | Worst Drop | At NS     | Category | Avg Change |
|---------------------------|------------|-----------|----------|------------|
| gpt-5.3-chat-latest       | +15pp      | NS=100    | Top Tier | +0.7pp     |
| o4-mini                   | -15pp      | NS=50/100 | Top Tier | -5.0pp     |
| o3-mini                   | -45pp      | NS=100    | Top Tier | -12.5pp    |
| gpt-5.2-chat-latest       | -30pp      | NS=100    | Top Tier | -6.7pp     |
| DeepSeek-R1               | -40pp      | NS=50     | Top Tier | -15pp      |
| claude-sonnet-4-5         | -90pp      | NS=10     | Mid Tier | -71.2pp    |
| grok-3                    | -85pp      | NS=10     | Mid Tier | -56.0pp    |
| claude-opus-4-6           | -50pp      | NS=20     | Mid Tier | -12.5pp    |
| gpt-5.4-mini              | -55pp      | NS=10     | Mid Tier | -42.5pp    |
| gpt-4o                    | -60pp      | NS=2      | Mid Tier | -40pp      |
| claude-haiku-4-5          | -55pp      | NS=5      | Low Tier | -41.7pp    |
| cohere-command-a          | -55pp      | NS=2      | Low Tier | -31.7pp    |

#### 2.4.3 Analysis by Performance Tier

**Top Tier: Reasoning-Optimized Models**
GPT-5.3-chat-latest stands alone as the only model that was essentially unaffected by the MOVING rule, and in fact improved at NS=100 (from 85% to 100%). This suggests GPT-5.3’s reasoning mechanisms can absorb a modest increase in per-step complexity without degradation, at least up to the point where its own drift threshold is reached. At NS=200 it showed a small decline (25% to 15%), consistent with its existing threshold behavior rather than MOVING-specific failure.
The remaining top-tier models (Kimi K2.5, o4-mini, o3-mini, GPT-5.2) showed consistent declines in the 5–45pp range at their critical threshold points. O3-mini was particularly affected, dropping 45pp at NS=100 (75% to 30%). GPT-5.2 lost 30pp at NS=100 (70% to 40%). These models retained their general shape of decay but their effective thresholds shifted leftward by one or two sequence-length steps.
DeepSeek-R1 and R1-0528 showed notable degradation even at short sequences (NS=2 and NS=5), unlike the OpenAI reasoning models which remained stable at those lengths. This suggests that DeepSeek’s reinforcement learning approach to reasoning is more fragile to rule-set changes than OpenAI’s Chain-of-Thought mechanisms.

**Mid Tier: The Catastrophic Collapse Group**
The most dramatic finding is the catastrophic collapse of mid-tier models. These are models that performed reasonably well in the original experiment (completing NS=10 or NS=20 with 50–95% success) but were devastated by the MOVING rule:
Claude-sonnet-4-5 experienced the single largest collapse: from 95% at NS=10 to just 5%, a 90pp drop. Its NS=5 performance fell from 80% to 15%, and it could not complete a single test at NS=20 (previously 85%). This model went from a credible mid-tier performer to near-total failure across almost every sequence length.
Grok-3 showed a similarly severe pattern, dropping from 90% to 10% at NS=5 and from 90% to 5% at NS=10. GPT-5.4-mini, GPT-4o, GPT-5.4-nano, and GPT-5-chat-latest all showed drops of 40–60pp at their critical operating points.
The Claude family was notably affected across the board. Claude-opus-4-6 dropped 50pp at NS=20 (95% to 45%). Claude-opus-4-1 lost 50pp at NS=20 (70% to 20%). The pattern is consistent: without purpose-built reasoning mechanisms, these models’ precision is extremely fragile to even minor increases in task complexity.

**Low Tier: Floor Effects Mask the Full Impact**
Models that were already struggling in the original experiment (cohere-command-a, grok-4-1-fast-non-reasoning, claude-sonnet-4-6) showed further declines, but the practical significance is limited since they were already near failure. The interesting observation is that even at NS=2, the simplest possible test, models like cohere-command-a dropped from 65% to 10%.

### 2.5 Conclusion

The MOVING rule experiment demonstrates:

- a single additional rule, adding one conditional check and one new output state, reduced the average completion rate by 22–25 percentage points at short sequence lengths (NS=2 through NS=10). The impact is disproportionate to the complexity added.

- the impact was overwhelmingly negative. At NS=2, 18 of 29 models declined and none improved. This confirms that the MOVING rule genuinely increases task difficulty rather than producing random variance.

- top-tier reasoning models (especially GPT-5.3) absorbed the additional complexity with minimal degradation, while mid-tier and lower-tier models experienced catastrophic collapse. The gap between reasoning-optimized and non-reasoning models widened dramatically.

## 3. Experiment 3: Isolating Decision Logic from Output Symbol Effects

### 3.1 Purpose

The goal of this experiment is to isolate the effect of decision logic from the influence of the output symbol alphabet. Specifically, it examines whether differences in model performance arise from the introduction of an additional logical rule, rather than from changes in the structure or size of the output vocabulary itself.
By aligning the output symbols with those used in Experiment 1 while retaining the logical structure of Experiment 2, this experiment ensures that any observed differences can be attributed to decision-making complexity rather than representational variation.

### 3.2 Approach

The approach follows Experiment 2 exactly, with one key modification. The rule remains the same: if the current move is "OK" and the previous move was also "OK", a special output is triggered. However, instead of outputting "MOVING", the system outputs "YIPEE".

This change ensures that the set of possible outputs—"OK," "YIPEE," "OUCH," and "BLOCKED"—matches that of Experiment 1. At the same time, the model must still apply the additional conditional rule based on the previous step’s output.

Importantly, this modification does not alter the board complexity, number of moves, prompt structure, or per-step classification difficulty. The only added requirement is tracking the immediately preceding output and applying a conditional rule, while keeping the output vocabulary consistent with earlier experiments.

### 3.3 Results Table

The table below presents the primary metric: proportion of 20 tests completed without any error, for each model at each sequence length. This is the “perfect test” binary measure.

| Model | NS=2 | NS=5 | NS=10 | NS=20 | NS=50 | NS=100 | NS=200 | NS=300 |
|-------|------|------|-------|-------|-------|--------|--------|--------|
| gpt-5.3-chat-latest | 100% | 100% | 100% | 100% | 100% | 90% | 20% | 0% |
| Kimi-K2.5 | 100% | 100% | 100% | 95% | 75% | 70% | 15% | 20% |
| o4-mini | 100% | 100% | 95% | 95% | 85% | 65% | 10% | 0% |
| gpt-5.2-chat-latest | 100% | 95% | 95% | 100% | 85% | 40% | 0% | 0% |
| o3-mini | 100% | 95% | 90% | 95% | 65% | 30% | 5% | 0% |
| model-router | 100% | 100% | 100% | 90% | 65% | 0% | 0% | 0% |
| grok-4-fast-reasoning | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model |
| DeepSeek-R1 | 100% | 95% | 95% | 100% | 60% | 20% | 5% | 0% |
| DeepSeek-R1-0528 | 100% | 100% | 100% | 100% | 25% | 0% | 0% | 0% |
| grok-3-mini | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model |
| grok-4-1-fast-reasoning | 100% | 100% | 100% | 90% | 75% | 20% | 0% | 0% |
| gpt-5.1-chat-latest | 100% | 100% | 95% | 75% | 0% | 0% | 0% | 0% |
| claude-opus-4-5 | 100% | 90% | 100% | 85% | 0% | 0% | 0% | 0% |
| claude-opus-4-6 | 100% | 90% | 60% | 35% | 0% | 0% | 0% | 0% |
| claude-sonnet-4-5 | 60% | 30% | 15% | 0% | 0% | 0% | 0% | 0% |
| claude-opus-4-1 | 85% | 65% | 50% | 50% | 0% | 0% | 0% | 0% |
| grok-3 | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model |
| gpt-5.4-mini | 45% | 20% | 5% | 0% | 0% | 0% | 0% | 0% |
| gpt-5-chat-latest | 80% | 50% | 20% | 0% | 0% | 0% | 0% | 0% |
| gpt-5.4-nano | 25% | 10% | 0% | 0% | 0% | 0% | 0% | 0% |
| gpt-4o | 45% | 5% | 0% | 0% | 0% | 0% | 0% | 0% |
| DeepSeek-V3.1 | 35% | 5% | 0% | 0% | 0% | 0% | 0% | 0% |
| DeepSeek-V3.2 | 40% | 20% | 0% | 0% | 0% | 0% | 0% | 0% |
| Mistral-Large-3 | 50% | 15% | 0% | 0% | 0% | 0% | 0% | 0% |
| claude-haiku-4-5 | 40% | 5% | 0% | 0% | 0% | 0% | 0% | 0% |
| Llama-4-Maverick-17B-128E-Instruct-FP8 | 50% | 5% | 0% | 0% | 0% | 0% | 0% | 0% |
| cohere-command-a | 30% | 15% | 0% | 0% | 0% | 0% | 0% | 0% |
| grok-4-1-fast-non-reasoning | 25% | 5% | 0% | 0% | 0% | 0% | 0% | 0% |
| claude-sonnet-4-6 | 25% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |

## 3.4 Conclusion

These results confirm the findings of the MOVING rule experiment.

- Introducing a single additional rule—requiring one extra conditional check on the previous step—again produces a large drop in performance, despite no increase in board complexity, prompt size, or per-step classification difficulty. This reinforces that even minimal increases in sequential reasoning requirements can have disproportionate effects.

- The negative impact remains systematic rather than random. As in the MOVING experiment, performance degradation is consistent across models, indicating that the added rule reliably increases task difficulty rather than introducing noise from output representation.

- Because the output vocabulary in this experiment is aligned with Experiment 1 (i.e., no additional output token such as "MOVING" is introduced), the degradation can be attributed purely to decision logic complexity, not to changes in the output symbol set.

Overall, this experiment isolates and confirms that the primary source of difficulty observed in the MOVING experiment is the incremental logical dependency, not the expansion of the output space.

## 4. Experiment 4: PURE PRECISION Experiment

### 4.1 Purpose

The purpose of this experiment is to increase the evaluation rigor of the original experiment (Experiment 1) by enforcing stricter validation of LLMs output. Specifically, it ensures that not only the response status (e.g., "OK") is correct, but also that the associated coordinates provided by LLMs are accurate.

### 4.2 Approach

This experiment is a re-run of the original experiment (Experiments 1) with an additional validation step. Previously, the evaluation logic only checked whether LLMs returned a correct status such as "OK", without verifying the correctness of the accompanying coordinates in the JSON output.

In this updated approach:

- The same experiment setup and rules are preserved.
- No changes are made to the model, prompts, or core logic.
- An additional validation layer is introduced to check that the returned coordinates exactly match the expected values.

For example, a response like "OK, 5, 4" would previously pass if the expected response was "OK, 6, 4", since only "OK" was validated. Under this new approach, such a response would fail due to incorrect coordinates.

### 4.3 Results Table

The table below presents the primary metric: proportion of 20 tests completed without any error, for each model at each sequence length. This is the “perfect test” binary measure.

| Model | NS=2 | NS=5 | NS=10 | NS=20 | NS=50 | NS=100 | NS=200 | NS=300 |
|-------|------|------|-------|-------|-------|--------|--------|--------|
| gpt-5.3-chat-latest | 100% | 100% | 100% | 100% | 95% | 95% | 20% | 0% |
| Kimi-K2.5 | 100% | 100% | 100% | 95% | 90% | 60% | 20% | 25% |
| o4-mini | 100% | 100% | 95% | 100% | 95% | 90% | 5% | 0% |
| gpt-5.2-chat-latest | 100% | 100% | 100% | 100% | 100% | 50% | 0% | 0% |
| o3-mini | 100% | 100% | 95% | 100% | 85% | 25% | 10% | 10% |
| model-router | 100% | 100% | 95% | 95% | 85% | 10% | 5% | 5% |
| grok-4-fast-reasoning | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model |
| DeepSeek-R1 | 100% | 100% | 100% | 100% | 75% | 15% | 0% | 0% |
| DeepSeek-R1-0528 | 100% | 100% | 100% | 100% | 25% | 0% | 0% | 0% |
| grok-3-mini | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model |
| grok-4-1-fast-reasoning | 100% | 95% | 100% | 100% | 90% | 5% | 0% | 0% |
| gpt-5.1-chat-latest | 100% | 100% | 95% | 85% | 0% | 0% | 0% | 0% |
| claude-opus-4-5 | 100% | 95% | 100% | 85% | 0% | 0% | 0% | 0% |
| claude-opus-4-6 | 100% | 85% | 90% | 90% | 0% | 0% | 0% | 0% |
| claude-sonnet-4-5 | 100% | 85% | 85% | 75% | 0% | 0% | 0% | 0% |
| claude-opus-4-1 | 90% | 85% | 80% | 80% | 0% | 0% | 0% | 0% |
| grok-3 | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model |
| gpt-5.4-mini | 85% | 70% | 75% | 15% | 0% | 0% | 0% | 0% |
| gpt-5-chat-latest | 85% | 60% | 35% | 10% | 0% | 0% | 0% | 0% |
| gpt-5.4-nano | 80% | 35% | 35% | 5% | 0% | 0% | 0% | 0% |
| gpt-4o | 65% | 35% | 15% | 0% | 0% | 0% | 0% | 0% |
| DeepSeek-V3.1 | 80% | 35% | 35% | 5% | 0% | 0% | 0% | 0% |
| DeepSeek-V3.2 | 75% | 50% | 40% | 10% | 5% | 0% | 0% | 0% |
| Mistral-Large-3 | 75% | 25% | 15% | 0% | 0% | 0% | 0% | 0% |
| claude-haiku-4-5 | 70% | 50% | 25% | 5% | 0% | 0% | 0% | 0% |
| Llama-4-Maverick-17B-128E-Instruct-FP8 | 50% | 20% | 20% | 0% | 0% | 0% | 0% | 0% |
| cohere-command-a | 55% | 25% | 20% | 5% | 0% | 0% | 0% | 0% |
| grok-4-1-fast-non-reasoning | 55% | 20% | 0% | 0% | 0% | 0% | 0% | 0% |
| claude-sonnet-4-6 | 100% | 30% | 0% | 0% | 0% | 0% | 0% | 0% |

## 4.4 Conclusion

The PURE PRECISION experiment enhances the reliability and strictness of the evaluation process without altering the original experimental design. By introducing coordinate-level validation, it ensures that LLMs must produce fully accurate responses rather than partially correct ones. This results in a more precise assessment of model performance and highlights discrepancies that were previously overlooked.

## 5. Experiment 5: CONDITION-PURE-CONDITION (CPC) Experiment

### 5.1 Purpose

The purpose of this experiment is to further explore and define the boundary conditions of an AI model’s reasoning and state transition capabilities. Building on insights from the PURE-CONDITION experiment, this new setup aims to test how the model handles layered rules and temporal dependencies (i.e., dependence on both current and previous states). By introducing an additional rule and symbol, the experiment seeks to evaluate whether the model can consistently track and apply multi-step logical conditions, thereby revealing limitations in memory, rule integration, and state awareness.

### 5.2 Approach

The approach modifies the existing MOVING experiment (Experiment 2) by introducing one additional rule. The system now operates with expanded logic that depends on both the present and past states. In this experiment, two new rules and one new symbol are added compared with the baseline (Experiment 1).

- Existing foundation: MOVING experiment rule:
  - **If current state is "OK" and previous state was "OK", then output "MOVING"**
- Additions: New rule definition:
  - **If current state is "OK" and previous state was "MOVING", then output "YIPEE"**

The experiment tests the model’s ability to:

- Track prior states accurately,
- Apply conditional logic across time steps,
- Integrate new rules without interfering with existing behavior.

### 5.3 Results Table

The table below presents the primary metric: proportion of 20 tests completed without any error, for each model at each sequence length. This is the “perfect test” binary measure.

| Model | NS=2 | NS=5 | NS=10 | NS=20 | NS=50 | NS=100 | NS=200 | NS=300 |
|-------|------|------|-------|-------|-------|--------|--------|--------|
| gpt-5.3-chat-latest | 100% | 100% | 100% | 100% | 100% | 85% | 5% | 0% |
| Kimi-K2.5 | 100% | 100% | 95% | 90% | 90% | 35% | 25% | 15% |
| o4-mini | 100% | 100% | 100% | 100% | 85% | 85% | 0% | 0% |
| gpt-5.2-chat-latest | 100% | 100% | 100% | 100% | 95% | 65% | 0% | 0% |
| o3-mini | 95% | 100% | 85% | 85% | 50% | 15% | 0% | 0% |
| model-router | 100% | 100% | 90% | 95% | 45% | 0% | 0% | 0% |
| grok-4-fast-reasoning | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model |
| DeepSeek-R1 | 100% | 95% | 95% | 95% | 55% | 15% | 0% | 0% |
| DeepSeek-R1-0528 | 100% | 100% | 85% | 80% | 60% | 5% | 0% | 0% |
| grok-3-mini | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model |
| grok-4-1-fast-reasoning | 100% | 100% | 100% | 90% | 30% | 5% | 0% | 0% |
| gpt-5.1-chat-latest | 100% | 100% | 85% | 35% | 0% | 0% | 0% | 0% |
| claude-opus-4-5 | 95% | 95% | 90% | 80% | 0% | 0% | 0% | 0% |
| claude-opus-4-6 | 95% | 100% | 30% | 0% | 0% | 0% | 0% | 0% |
| claude-sonnet-4-5 | 65% | 50% | 40% | 10% | 0% | 0% | 0% | 0% |
| claude-opus-4-1 | 85% | 70% | 70% | 30% | 0% | 0% | 0% | 0% |
| grok-3 | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model | Retired model |
| gpt-5.4-mini | 55% | 25% | 5% | 5% | 0% | 0% | 0% | 0% |
| gpt-5-chat-latest | 75% | 25% | 10% | 0% | 0% | 0% | 0% | 0% |
| gpt-5.4-nano | 30% | 5% | 0% | 0% | 0% | 0% | 0% | 0% |
| gpt-4o | 40% | 5% | 0% | 0% | 0% | 0% | 0% | 0% |
| DeepSeek-V3.1 | 85% | 5% | 0% | 0% | 0% | 0% | 0% | 0% |
| DeepSeek-V3.2 | 70% | 5% | 0% | 0% | 0% | 0% | 0% | 0% |
| Mistral-Large-3 | 65% | 10% | 0% | 0% | 0% | 0% | 0% | 0% |
| claude-haiku-4-5 | 65% | 5% | 10% | 0% | 0% | 0% | 0% | 0% |
| Llama-4-Maverick-17B-128E-Instruct-FP8 | 30% | 5% | 0% | 0% | 0% | 0% | 0% | 0% |
| cohere-command-a | 50% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |
| grok-4-1-fast-non-reasoning | 45% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |
| claude-sonnet-4-6 | 15% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |

## 5.4 Conclusion

The CONDITION-PURE-CONDITION experiment provides a more demanding test of an AI model’s ability to reason over sequential states and layered rules. The addition of a temporal dependency (linking previous and current states) exposes whether the model can maintain coherent internal state tracking. Overall, this experiment helps more precisely define the boundary at which the AI model begins to struggle with compounded logical structures.
