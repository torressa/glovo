Stochastic Optimisation
=======================

Given the stochastic nature of the problem I decided to try and
implement some stochastic optimisation techniques. After some research,
I decided that the literature stream that best fitted the problem is the
stochastic machine scheduling problem. Particularly, I borrowed some of
the concepts in [@LI2017263] (included in `/files/`) to formulate and
solve the problem using scenario generation.

Modelling
=========

Notation
--------

### Sets {#sets .unnumbered}

$\mathcal{G}$:

:   Set of glovers $\mathcal{G} = \{1,2,\dots,G\}$;

$\mathcal{T}$:

:   Set of slots $\mathcal{T} = \{1,2,\dots,T\}$;

$\mathcal{S}$:

:   Set of scenarios $\mathcal{S} = \{1,2,\dots,S\}$.

### Parameters {#parameters .unnumbered}

$\text{st}_t/\text{et}_t$:

:   Start/end time of slot $t$;

$p_s$:

:   Probability associated with scenario $s$;

$\text{PL}_{ts}$:

:   Sample $\{0,1\}$ from leaving distribution for slot $t$ under
    scenario $s$;

$D_{ts}$:

:   Order demand for slot $t$ under scenario $s$;

$\tau_{ts}$:

:   Delivery duration for a single delivery in slot $t$ under scenario
    $s$;

### Variables {#variables .unnumbered}

$x_{gt}$:

:   Binary variable with value 1 if glover $g$ is assigned to a delivery
    in slot $t$, 0 otherwise;

$z_{ts}$:

:   Binary variable (auxiliary) with value 1 if glover $g$ begins their
    shift in slot $t$, 0 otherwise;

$Z_{gts}$:

:   Binary variable with value 1 if glover $g$ leaves (finishes
    their shift) after slot $t$ under scenario $s$, 0 otherwise;

$Q^F_{ts}$:

:   Continuous variable representing the number of orders **fulfilled**
    in slot $t$ under scenario $s$;

$Q^C_{ts}$:

:   Continuous variable representing the number of orders **cancelled**
    in slot $t$ under scenario $s$;

$$\begin{aligned}
    &\ \textbf{min}~~ \sum_s p_s \left(10 \text{CR} - \text{UR}\right)&~ & \label{eq:obj}\\
    &\ \textbf{subject to}\nonumber \\
    &\ \textbf{Orders}\nonumber\\
    &\  Q^C_{ts} \leq Q^F_{ts}  &~ & \forall t,s \label{eq:ordersCF}\\
    &\ \sum_g x_{gt} \leq Q^F_{ts}  &~ & \forall t,s \label{eq:ordersF}\\
    &\ \textbf{Demand}\nonumber\\
    &\ \sum_g x_{gt} \geq D_{ts}  &~ & \forall t,s \label{eq:demand}\\
    &\ \textbf{Delivery Duration} &~ &\nonumber\\
    &\ x_{gt}\leq x_{gt'}  &~ & \forall g, t,\{t':\text{st}_t<\text{st}_{t'} < \text{et}_t\} \label{eq:duration}\\
    &\ \textbf{Glovers Leaving}\nonumber\\
    &\ Z_{gts} \geq \text{PL}_{ts} &~ & \forall g, t, s \label{eq:randomZ}\\
    % &\ Z_{g,t-1,s} \leq Z_{gts} &~ & \forall g, t, s \label{eq:recZ}\\
    &\ x_{gt'} \leq 1-Z_{gts} &~ & \forall g, t, s, t'=\inf\{t':~\text{et}_t\leq\text{st}_{t'}\} \label{eq:XZ}\\
    % &\ 1-y_{gt} \leq x_{gt} &~ & \forall g, t \label{eq:XY}\\
    &\ \textbf{Transitivity (consecutive values)}\nonumber\\
    &\ z_{gt_0} \geq x_{g t_0} &~ & \forall g \label{eq:transitivityInit}\\
    &\ z_{gt} \geq x_{gt} - x_{g,t-1} &~ & \forall g, t \label{eq:transitivity}\\
    &\ \sum_t z_{gt} \leq 1 &~ & \forall g \label{eq:transitivitySum}\\
    &\ \textbf{Variable Definitions}\nonumber\\
    &\ x_{gt}, z_{gt}\in\{0,1\} &~ & \forall g, t \label{eq:binaryDef}\\
    &\ Z_{gts}\in\{0,1\} &~ & \forall g, t, s \label{eq:binaryDefZ}\\
    &\ Q_{ts}^F, Q_{ts}^C\in\mathbb{R}^+ &~ & \forall t, s \label{eq:continuousDef}\end{aligned}$$

Where the objective function components are,
$$\text{CR} = \frac{\sum_t Q^C_{ts}}{\sum_t Q^F_{ts}}$$ and,
$$\text{UR} = \frac{\sum_g\sum_t \tau_{ts} x_{gt}}{\sum_g \sum_t -\left[\text{st}_t (x_{gt}-x_{g,t-1}) - \tau_{ts}Z_{gts}\right]}.$$
The numerator of UR corresponds to the cumulative working time and the
denominator to the shift duration. For the denominator to represent the
shift duration, I have made a transitivity assumption, that is, glovers
have continuous shifts. The shifts can be of any duration, but they
cannot leave and come back on the same day. With this in mind, the
difference between the $x$ variables will either be $1$ at the start of
the shift, $0$ during the shift and $-1$ at the end. Hence, for a shift
starting at $t_0$ and ending at $t_L$, we have
$$-[\text{st}_{t_0} + 0 + \dots + 0 - \text{st}_{t_L} - \tau_{t_L}]=-[\text{st}_{t_0}- \text{st}_{t_L} - (\text{et}_{t_L}-\text{st}_{t_L})] = \text{et}_{t_L}-\text{st}_{t_0}.$$

Constraint ensure that the number of fulfilled orders is greater than
the number of cancelled orders (this keeps the CR term in the objective
function less than 1). Constraint counts the number of orders completed.
Constraint ensures that demand per slot is met. Constraint ensures that
until an order is completed, the glover cannot leave. Constraint sets
the leaving variable to 1 or 0 with the corresponding probability for
that slot. Constraint ensures that if the glover leaves, they cannot be
allocated any more slots. By forcing the $x$ variable to be 0 once the
glover leaves and given that the transitivity constraints in place, this
ensures that the glover cannot be allocated more slots. Constraints –
enforce the continuous shift idea.

Scenario Generation
-------------------

![Example scenario for a single day showing order demand data. The data
is approximated and the sampled are drawn. Data is shown red and the
samples in blue and the variance is shown in grey.<span
data-label="fig:singleDay"></span>](Figure_1.png){width="70.00000%"}

For each scenario, we sample from different fitted distributions to the
data. I used the `PyMC3` package and `numpy` for this purpose. The order
demand, is estimated using a pricing strategy in [@pymc] which, in a
Bayesian framework, uses random walk and normal distributions to fit the
trend. I also used a simple binomial to sample the leaving probability.
I used the command `numpy.random.binomial(1,p)` where `p` is the
probability of leaving. This gives me a $\{0,1\}$ bound which fixes my
final shift variable, $Z$. Finally, for the probability for each
scenario occuring, $p_s$, I sample from a random Uniform distribution by
using `numpy.random.uniform(0,1)`.

Implementation and Discussion
=============================

Solving nonlinear models is really time consuming, if, like me, you are
solving instances on standard machines, I suggest you try to find a work
around to make your formulation linear. This will allow for multiple
scenarios to be run, and with a similar objective function, you can
obtain more information about the total number of glovers required for a
city. In my first solution, I have formulated the nonlinear objective
function as two quadratic constraints by adding some additional
variables, however, it takes a really long time to arrive at an optimal
solution even for a single scenario. Please note that I wasn’t able to
implement all of the constraints specified for the test. Furthermore,
constraints and regarding the orders make the problem unbounded.
Particularly, it makes the matrix $Q$ associated with the quadratic
constraints not positive semi-definite, hence, the solution space is not
convex.

Alternatively, I have implemented the following multi-objective linear
program. Which removes of the restrictive transitivity assumption and
allows us to solve the problem to optimality for multiple scenarios.
Additionally, a lexicographic approach removes the need to set arbitrary
weights in the objective function coefficients.

$$\begin{aligned}
    &\ \textbf{min}~~ \sum_s \sum_g \sum_t p_{s} e_{gts}&~ & \label{eq:obj1}\\
    &\ \textbf{min}~~ \sum_s \sum_g \sum_t p_{s} x_{gts}&~ & \label{eq:obj2}\\
    &\ \textbf{subject to}\nonumber \\
%   &\ \textbf{Orders}\nonumber\\
%   &\  Q^C_{ts} \leq Q^F_{ts}  &~ & \forall t,s \label{eq:ordersCF}\\
%   &\ \sum_g x_{gt} \leq Q^F_{ts}  &~ & \forall t,s \label{eq:ordersF}\\
    &\ \textbf{Demand}\nonumber\\
    &\ \sum_g x_{gt} + e_{ts} \geq D_{ts}  &~ & \forall t,s \label{eq:demand2}\\
    &\ \textbf{Delivery Duration} &~ &\nonumber\\
    &\ x_{gt'}\leq 1 - x_{gt}  &~ & \forall g, t,\{t':\text{st}_t<\text{st}_{t'} < \text{et}_t\} \label{eq:duration2}\\
    &\ \textbf{Glovers Leaving}\nonumber\\
    &\ \eqref{eq:randomZ} \text{ and } \eqref{eq:XZ} \nonumber\\
    % &\ 1-y_{gt} \leq x_{gt} &~ & \forall g, t \label{eq:XY}\\
    % &\ \textbf{Transitivity (consecutive values)}\nonumber\\
    % &\ z_{gt_0} \geq x_{g t_0} &~ & \forall g \label{eq:transitivityInit}\\
    % &\ z_{gt} \geq x_{gt} - x_{g,t-1} &~ & \forall g, t \label{eq:transitivity}\\
    % &\ \sum_t z_{gt} \leq 1 &~ & \forall g \label{eq:transitivitySum}\\
    &\ \textbf{Variable Definitions}\nonumber\\
    &\ x_{gt}, z_{gt}\in\{0,1\} &~ & \forall g, t \label{eq:binaryDef2}\\
    &\ e_{ts}\in\{0,1\} &~ & \forall  t,s \label{eq:binaryDefe2}\\
    &\ Z_{gts}\in\{0,1\} &~ & \forall g, t, s \label{eq:binaryDefZ2}\\
    &\ e_{ts} \in\mathbb{R}^+ &~ & \forall t, s \label{eq:continuousDef2}\end{aligned}$$

Where $M$ is a big number and $e_{ts}$ is a new continuous variable that
represents some emergency glovers that can be called for a given
delivery. The only new constraint here is the delivery duration
constraint which ensures that a glover is not assigned another slot
until it delivers its previous task.

Results show, using this approach, you can compute a robust solution
across multiple different scenarios really quickly. Figure
\[fig:my\_label\] shows the number of glovers required per slot in order
to meet the variable demand for 5 different scenarios. The solution time
for this case was just 20 seconds. Solution time for 10 scenarios is 27
seconds. Whereas, 30 scenarios take around 16 minutes and 50 scenarios
crashed my machine.

However, I haven’t implemented all of the constraints required. This is
likely to slow down the model, specially if there are a lot of
additional variables. I think these models allow such extensions to be
made easily, I simply didn’t have the time. Espero que os sirva de algo!

![Number of glovers allocated per slot for 5 different scenarios.<span
data-label="fig:my_label"></span>](results.eps){width="90.00000%"}
