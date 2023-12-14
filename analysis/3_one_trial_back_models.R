library(Matrix)
library(tidyverse)
library(brms)
library(tidybayes)
library(broom.mixed)

# How many iterations to run models
model_iter = 2000

# put a prior on the beta coefficients (brms uses a flat prior by default)
beta_prior = c(prior_string("student_t(3, 0, 10)", class = "b"))

load('clean_data/combined_data_for_models.rda')

# Stage 1 Models ----------------------------------------------------------

# Run models
stage1_models = combined_data_for_models %>%
  group_by(cohort) %>%
  nest() %>%
  mutate(model = purrr::map(data, ~brms::brm(data = ., stay1 ~ last_reward*last_transition + (last_reward*last_transition|id),
                                             family= bernoulli(link = 'logit'), chains = 4, cores = 4, iter = model_iter, prior=beta_prior)))

# Extract coefficients
stage1_model_coefs = stage1_models %>%
  mutate(coefs = purrr::map(model,
                            ~broom.mixed::tidy(.))) %>%
  dplyr::select(-model, -data) %>%
  unnest(coefs)

# Extract posterior predictions
stage1_model_posterior_preds = stage1_models %>%
  mutate(preds = purrr::map(model,
                            ~tidybayes::add_epred_draws(newdata = expand.grid(last_reward = 0:1, 
                                                                              last_transition = c('rare', 'common')),
                                                        object=., re_formula = NA))) %>%
  dplyr::select(-model, -data) %>%
  unnest(preds)

# Save outputs
save(stage1_models, file = '../results/stage1_models.rda')
save(stage1_model_coefs, stage1_model_posterior_preds, file = '../results/stage1_coefs_preds.rda')

rm(stage1_models)
gc()

stage1_models_centered = combined_data_for_models %>%
  mutate(last_reward = ifelse(last_reward == 0, -0.5, 0.5),
         last_transition = ifelse(last_transition=='rare', -0.5, 0.5)) %>%
  group_by(cohort) %>%
  nest() %>%
  mutate(model = purrr::map(data, ~brms::brm(data = ., stay1 ~ last_reward*last_transition + (last_reward*last_transition|id),
            family= bernoulli(link = 'logit'), chains = 4, cores = 4, iter = model_iter, prior=beta_prior)))


stage1_model_coefs_centered = stage1_models_centered %>%
  mutate(coefs = purrr::map(model,
                            ~broom.mixed::tidy(.))) %>%
  dplyr::select(-model, -data) %>%
  unnest(coefs)

save(stage1_model_coefs_centered, file = '../results/stage1_coefs_centered.rda')

# Stage 2 Models ----------------------------------------------------------
# Run models
stage2_models = combined_data_for_models %>%
  group_by(cohort) %>%
  nest() %>%
  mutate(model = purrr::map(data, ~brms::brm(data = ., stay2 ~ last_reward*state_match + (last_reward*state_match|id),
            family= bernoulli(link = 'logit'), chains = 4, cores = 4, iter = model_iter, prior=beta_prior)))

# Extract coefficients
stage2_model_coefs = stage2_models %>%
  mutate(coefs = purrr::map(model,
                            ~broom.mixed::tidy(.))) %>%
  dplyr::select(-model, -data) %>%
  unnest(coefs)

# Extract posterior predictions
stage2_model_posterior_preds = stage2_models %>%
  mutate(preds = purrr::map(model,
                            ~tidybayes::add_epred_draws(newdata = expand.grid(last_reward = 0:1, 
                                                                                state_match = c('Same State', 'Different State')),
                            object=., re_formula = NA))) %>%
  dplyr::select(-model, -data) %>%
  unnest(preds)

# Save outputs
save(stage2_models, file = '../results/stage2_models.rda')
save(stage2_model_coefs, stage2_model_posterior_preds, file = '../results/stage2_coefs_preds.rda')

# Stage 2 --> Next Trial Stage 1 Models

# Run models
next_trial_seq_models = combined_data_for_models %>%
  group_by(cohort) %>%
  nest() %>%
  mutate(model = purrr::map(data, ~brms::brm(data = ., next_match_button ~ last_reward + (last_reward | id),
            family= bernoulli(link = 'logit'), chains = 4, cores = 4, iter = model_iter, prior=beta_prior)))

# Extract Coefficients
next_trial_seq_model_coefs = next_trial_seq_models %>%
  mutate(coefs = purrr::map(model,
                            ~broom.mixed::tidy(.))) %>%
  dplyr::select(-model, -data) %>%
  unnest(coefs)

# Extract Posterior Predictions
next_trial_seq_model_posterior_preds = next_trial_seq_models %>%
  mutate(preds = purrr::map(model,
                            ~tidybayes::add_epred_draws(newdata = expand.grid(last_reward = 0:1, 
                                                                                state_match = c('Same State', 'Different State')),
                            object=., re_formula = NA))) %>%
  dplyr::select(-model, -data) %>%
  unnest(preds)

# Save outputs
save(next_trial_seq_models, file = '../results/next_trial_seq_models.rda')
save(next_trial_seq_model_coefs, next_trial_seq_model_posterior_preds, file = '../results/next_trial_seq_coefs_preds.rda')