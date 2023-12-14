library(rstan)
library(tidyverse)
options(mc.cores = parallel::detectCores())

n_iter = 4000

# Potter ------------------------------------------------------------------

# Load in data matrices
load('clean_data/potter_data_for_rl_model.rda')

# format data for stan model
stan_data_list_potter = list(N = nrow(potter_choice_1_matrix), 
                     T = ncol(potter_choice_1_matrix), 
                     Tsubj = rep(ncol(potter_choice_1_matrix), nrow(potter_choice_1_matrix)), 
                     level1_choice = potter_choice_1_matrix, 
                     level2_choice = potter_choice_2_matrix,
                     reward = potter_reward_matrix, 
                     missing = potter_missing_matrix,
                     trans_prob = .7)

# fit models & save
fit_spatiomotor_only_potter = stan(file = 'models/spatiomotor_only.stan', data = stan_data_list_potter, chains =4, iter =n_iter)
fit_mbmf_only_potter = stan(file = 'models/mbmf_only.stan', data = stan_data_list_potter, chains =4, iter =n_iter)
fit_mbmf_spatiomotor_potter = stan(file = 'models/mbmf_spatiomotor.stan', data = stan_data_list_potter, chains =4, iter =n_iter)
fit_mbmf_spatiomotor2_potter = stan(file = 'models/mbmf_spatiomotor2.stan', 
                           data = stan_data_list_potter, chains =4, iter =n_iter)

loo_spatiomotor_only_potter = loo(fit_spatiomotor_only_potter)
loo_mbmf_only_potter= loo(fit_mbmf_only_potter)
loo_mbmf_spatiomotor_potter= loo(fit_mbmf_spatiomotor_potter)
loo_mbmf_spatiomotor2_potter=loo(fit_mbmf_spatiomotor2_potter)
potter_comparison = loo::loo_compare(loo_spatiomotor_only_potter, loo_mbmf_only_potter, loo_mbmf_spatiomotor_potter, loo_mbmf_spatiomotor2_potter)

save(potter_comparison, loo_spatiomotor_only_potter, loo_mbmf_only_potter, loo_mbmf_spatiomotor_potter, loo_mbmf_spatiomotor2_potter, file = '../results/potter_model_comparison.rda')
save(fit_mbmf_only_potter, fit_mbmf_spatiomotor_potter, fit_mbmf_spatiomotor2_potter, fit_spatiomotor_only_potter, file = '../results/potter_models.rda')
rm(fit_mbmf_only_potter, fit_mbmf_spatiomotor_potter, fit_mbmf_spatiomotor2_potter, fit_spatiomotor_only_potter)
gc()

# Decker ------------------------------------------------------------------

# Load in data matrices
load('clean_data/decker_data_for_rl_model.rda')

# format data for stan model
stan_data_list_decker = list(N = nrow(decker_choice_1_matrix), 
                     T = ncol(decker_choice_1_matrix), 
                     Tsubj = rep(ncol(decker_choice_1_matrix), nrow(decker_choice_1_matrix)), 
                     level1_choice = decker_choice_1_matrix, 
                     level2_choice = decker_choice_2_matrix,
                     reward = decker_reward_matrix, 
                     missing = decker_missing_matrix,
                     trans_prob = .7)

# fit models & save
fit_spatiomotor_only_decker = stan(file = 'models/spatiomotor_only.stan', data = stan_data_list_decker, chains =4, iter =n_iter)
fit_mbmf_only_decker = stan(file = 'models/mbmf_only.stan', data = stan_data_list_decker, chains =4, iter =n_iter)
fit_mbmf_spatiomotor_decker = stan(file = 'models/mbmf_spatiomotor.stan', data = stan_data_list_decker, chains =4, iter =n_iter)
fit_mbmf_spatiomotor2_decker = stan(file = 'models/mbmf_spatiomotor2.stan', 
                           data = stan_data_list_decker, chains =4, iter =n_iter)

loo_spatiomotor_only_decker = loo(fit_spatiomotor_only_decker)
loo_mbmf_only_decker= loo(fit_mbmf_only_decker)
loo_mbmf_spatiomotor_decker= loo(fit_mbmf_spatiomotor_decker)
loo_mbmf_spatiomotor2_decker=loo(fit_mbmf_spatiomotor2_decker)
decker_comparison = loo::loo_compare(loo_spatiomotor_only_decker, loo_mbmf_only_decker, loo_mbmf_spatiomotor_decker, loo_mbmf_spatiomotor2_decker)

save(decker_comparison, loo_spatiomotor_only_decker, loo_mbmf_only_decker, loo_mbmf_spatiomotor_decker, loo_mbmf_spatiomotor2_decker, file = '../results/decker_model_comparison.rda')
save(fit_mbmf_only_decker, fit_mbmf_spatiomotor_decker, fit_mbmf_spatiomotor2_decker, fit_spatiomotor_only_decker, file = '../results/decker_models.rda')
rm(fit_mbmf_only_decker, fit_mbmf_spatiomotor_decker, fit_mbmf_spatiomotor2_decker, fit_spatiomotor_only_decker)
gc()

# Online ------------------------------------------------------------------

# Load in data matrices
load('clean_data/online_data_for_rl_model.rda')

# format data for stan model
stan_data_list_online = list(N = nrow(online_choice_1_matrix), 
                     T = ncol(online_choice_1_matrix), 
                     Tsubj = rep(ncol(online_choice_1_matrix), nrow(online_choice_1_matrix)), 
                     level1_choice = online_choice_1_matrix, 
                     level2_choice = online_choice_2_matrix,
                     reward = online_reward_matrix, 
                     missing = online_missing_matrix,
                     trans_prob = .7)

# fit models & save
fit_spatiomotor_only_online = stan(file = 'models/spatiomotor_only.stan', data = stan_data_list_online, chains =4, iter =n_iter)
fit_mbmf_only_online = stan(file = 'models/mbmf_only.stan', data = stan_data_list_online, chains =4, iter =n_iter)
fit_mbmf_spatiomotor_online = stan(file = 'models/mbmf_spatiomotor.stan', data = stan_data_list_online, chains =4, iter =n_iter)
fit_mbmf_spatiomotor2_online = stan(file = 'models/mbmf_spatiomotor2.stan', 
                           data = stan_data_list_online, chains =4, iter =n_iter)

loo_spatiomotor_only_online = loo(fit_spatiomotor_only_online)
loo_mbmf_only_online= loo(fit_mbmf_only_online)
loo_mbmf_spatiomotor_online= loo(fit_mbmf_spatiomotor_online)
loo_mbmf_spatiomotor2_online=loo(fit_mbmf_spatiomotor2_online)
online_comparison = loo::loo_compare(loo_spatiomotor_only_online, loo_mbmf_only_online, loo_mbmf_spatiomotor_online, loo_mbmf_spatiomotor2_online)

save(online_comparison, loo_spatiomotor_only_online, loo_mbmf_only_online, loo_mbmf_spatiomotor_online, loo_mbmf_spatiomotor2_online, file = '../results/online_model_comparison.rda')
save(fit_mbmf_only_online, fit_mbmf_spatiomotor_online, fit_mbmf_spatiomotor2_online, fit_spatiomotor_only_online, file = '../results/online_models.rda')
rm(fit_mbmf_only_online, fit_mbmf_spatiomotor_online, fit_mbmf_spatiomotor2_online, fit_spatiomotor_only_online)
gc()

# DANL ------------------------------------------------------------------

# Load in data matrices
load('clean_data/danl_data_for_rl_model.rda')

# make DANL missing matrix
danl_missing_matrix = danl_reward_matrix
danl_missing_matrix[danl_reward_matrix < 2] = 0

# format data for stan model
stan_data_list_danl = list(N = nrow(danl_choice_1_matrix), 
                     T = ncol(danl_choice_1_matrix), 
                     Tsubj = rep(ncol(danl_choice_1_matrix), nrow(danl_choice_1_matrix)), 
                     level1_choice = danl_choice_1_matrix, 
                     level2_choice = danl_choice_2_matrix,
                     reward = danl_reward_matrix, 
                     missing = danl_missing_matrix,
                     trans_prob = .7)

# fit models & save
fit_spatiomotor_only_danl = stan(file = 'models/spatiomotor_only.stan', data = stan_data_list_danl, chains =4, iter =n_iter)
fit_mbmf_only_danl = stan(file = 'models/mbmf_only.stan', data = stan_data_list_danl, chains =4, iter =n_iter)
fit_mbmf_spatiomotor_danl = stan(file = 'models/mbmf_spatiomotor.stan', data = stan_data_list_danl, chains =4, iter =n_iter)
fit_mbmf_spatiomotor2_danl = stan(file = 'models/mbmf_spatiomotor2.stan', 
                           data = stan_data_list_danl, chains =4, iter =n_iter)

loo_spatiomotor_only_danl = loo(fit_spatiomotor_only_danl)
loo_mbmf_only_danl= loo(fit_mbmf_only_danl)
loo_mbmf_spatiomotor_danl= loo(fit_mbmf_spatiomotor_danl)
loo_mbmf_spatiomotor2_danl=loo(fit_mbmf_spatiomotor2_danl)
danl_comparison = loo::loo_compare(loo_spatiomotor_only_danl, loo_mbmf_only_danl, loo_mbmf_spatiomotor_danl, loo_mbmf_spatiomotor2_danl)

save(danl_comparison, loo_spatiomotor_only_danl, loo_mbmf_only_danl, loo_mbmf_spatiomotor_danl, loo_mbmf_spatiomotor2_danl, file = '../results/danl_model_comparison.rda')
save(fit_mbmf_only_danl, fit_mbmf_spatiomotor_danl, fit_mbmf_spatiomotor2_danl, fit_spatiomotor_only_danl, file = '../results/danl_models.rda')
rm(fit_mbmf_only_danl, fit_mbmf_spatiomotor_danl, fit_mbmf_spatiomotor2_danl, fit_spatiomotor_only_danl)
