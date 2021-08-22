# Counterfactual-storyRW

Counterfactual story rewriting with Structural Causal Model

[TimeTravel](https://arxiv.org/abs/1909.04076): dataset [download](https://drive.google.com/file/d/150jP5FEHqJD3TmTO_8VGdgqBftTDKn4w/view?usp=sharing)  
[ASER](https://hkust-knowcomp.github.io/ASER/html/index.html#): Event graph  
Stractural Causal Model  
ELMo: Tools to compute event representatation  

## 3-Steps to make counterfactual story rewriting with SCM

1. Compute event distribution $E_i \sim N(\mu_i, \sigma_i)$ of sentence $i$ based on original story.  
Distribution are **weighted** to frequence fetched from ASER, an event graph.
2. Use **Variational Inference** technology to estimate the approximation of the situation variables $U_i$ of sentence $i$ given the original story, so that $(U_i|E_0,E_1,...,E_{4})\sim N(g^*, h^*)$. Plus, we express $g, h$ as neural networks.
3. Iteratively update weights $w_{ij}$ of SCM with situation $U_i$ and adjacent event representation $e_{i-1,j}, e_{i, k}$. Specifically, $w_{ij}=[e_i||u]w[e_j||u]^T$.  
Make **causal inference** on $(\hat{E_i}|U_i,E_0,E_1,...,E_{i-1})$ with Structure Causal Model.

In step 2,  
Variational AutoEncoder:
$X \stackrel{Encoder}{\longrightarrow} Z \stackrel{Decoder}{\longrightarrow} Y $  
where $X=[E_0,...,E_{i-1}], Z=[U], Y=[E_i]$  
$$
\begin{aligned}
Loss_i &= L_{reconstruction-term} + L_{regularisation-term}\\
&=E[logP(E_i|U_i,E_0,...,E_{i-1})]-KL[q(U_i|E_0,...,E_{i-1})||P(U_i)]\\
&=Const*||y-\hat{y}||+KL[N(g(x), h(x))||N(0,1)]
\end{aligned}
$$
where
$P(E_i|U_i,E_0,...,E_{i-1})\sim N(f(z),cI), q(U_i|E_0,...,E_{i-1})\sim N(g(x),h(x)),P(U_i)\sim N(0,I)$  
We can express $f, g, h$ as neural networks.

$(g^*, h^*)=argmin \sum Loss_i$
