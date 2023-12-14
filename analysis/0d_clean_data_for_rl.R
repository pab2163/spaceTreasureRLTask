library(tidyverse)


# Clean DANL Data ---------------------------------------------------------
space_data = read_csv('../data/danl_space_treasure_comps.csv')

space_data_for_rl_model = space_data %>%
  dplyr::select(id, trial, choice_1, choice_2, reward, state) %>%
  mutate(choice_2 = ifelse(state=='B', choice_2+3, choice_2+1),
         choice_1 = choice_1 + 1)


danl_choice_1_matrix = space_data_for_rl_model %>%
  select(., id, choice_1, trial) %>%
  tidyr::spread(., key = id, value = choice_1) %>%
  select(., -trial) %>%
  t()

danl_choice_2_matrix = space_data_for_rl_model %>%
  select(., id, choice_2, trial) %>%
  tidyr::spread(., key = id, value = choice_2) %>%
  select(., -trial) %>%
  t()

danl_reward_matrix = space_data_for_rl_model %>%
  select(., id, reward, trial) %>%
  tidyr::spread(., key = id, value = reward) %>%
  select(., -trial) %>%
  t()


save(danl_choice_1_matrix, danl_choice_2_matrix, danl_reward_matrix, file = 'clean_data/danl_data_for_rl_model.rda')



# Clean Hartley Data ------------------------------------------------------

hartley = read_csv('../data/hartley_lag.csv') %>%
  dplyr::filter(age <=14)

hartley_data_for_rl_model = hartley %>%
  dplyr::select(id, trial_num, choice_1, choice_2, reward, state, cohort) %>%
  mutate(choice_2 = ifelse(state=='B', choice_2+3, choice_2+1),
         choice_1 = choice_1 + 1,
         missing = ifelse(is.na(choice_1) | is.na(choice_2) | is.na(reward), 1, 0))

## Potter
potter_choice_1_matrix = hartley_data_for_rl_model %>%
  dplyr::filter(cohort == 'potter') %>%
  select(., id, choice_1, trial_num) %>%
  tidyr::spread(., key = id, value = choice_1) %>%
  select(., -trial_num) %>%
  t()

potter_choice_2_matrix = hartley_data_for_rl_model %>%
  dplyr::filter(cohort == 'potter') %>%
  select(., id, choice_2, trial_num) %>%
  tidyr::spread(., key = id, value = choice_2) %>%
  select(., -trial_num) %>%
  t()

potter_reward_matrix = hartley_data_for_rl_model %>%
  dplyr::filter(cohort == 'potter') %>%
  select(., id, reward, trial_num) %>%
  tidyr::spread(., key = id, value = reward) %>%
  select(., -trial_num) %>%
  t()

potter_missing_matrix = hartley_data_for_rl_model %>%
  dplyr::filter(cohort == 'potter') %>%
  select(., id, missing, trial_num) %>%
  tidyr::spread(., key = id, value = missing) %>%
  select(., -trial_num) %>%
  t()

potter_choice_1_matrix[is.na(potter_choice_1_matrix)] = 1
potter_choice_2_matrix[is.na(potter_choice_2_matrix)] = 1
potter_reward_matrix[is.na(potter_reward_matrix)] = 1
potter_missing_matrix[is.na(potter_missing_matrix)] = 1


save(potter_choice_1_matrix, potter_missing_matrix, potter_reward_matrix, potter_choice_2_matrix,
     file = 'clean_data/potter_data_for_rl_model.rda')

## Decker
decker_choice_1_matrix = hartley_data_for_rl_model %>%
  dplyr::filter(cohort == 'decker') %>%
  select(., id, choice_1, trial_num) %>%
  tidyr::spread(., key = id, value = choice_1) %>%
  select(., -trial_num) %>%
  t()

decker_choice_2_matrix = hartley_data_for_rl_model %>%
  dplyr::filter(cohort == 'decker') %>%
  select(., id, choice_2, trial_num) %>%
  tidyr::spread(., key = id, value = choice_2) %>%
  select(., -trial_num) %>%
  t()

decker_reward_matrix = hartley_data_for_rl_model %>%
  dplyr::filter(cohort == 'decker') %>%
  select(., id, reward, trial_num) %>%
  tidyr::spread(., key = id, value = reward) %>%
  select(., -trial_num) %>%
  t()

decker_missing_matrix = hartley_data_for_rl_model %>%
  dplyr::filter(cohort == 'decker') %>%
  select(., id, missing, trial_num) %>%
  tidyr::spread(., key = id, value = missing) %>%
  select(., -trial_num) %>%
  t()

decker_choice_1_matrix[is.na(decker_choice_1_matrix)] = 1
decker_choice_2_matrix[is.na(decker_choice_2_matrix)] = 1
decker_reward_matrix[is.na(decker_reward_matrix)] = 1
decker_missing_matrix[is.na(decker_missing_matrix)] = 1


save(decker_choice_1_matrix, decker_missing_matrix, decker_reward_matrix, decker_choice_2_matrix,
     file = 'clean_data/decker_data_for_rl_model.rda')



## Online
online_choice_1_matrix = hartley_data_for_rl_model %>%
  dplyr::filter(cohort == 'online') %>%
  select(., id, choice_1, trial_num) %>%
  tidyr::spread(., key = id, value = choice_1) %>%
  select(., -trial_num) %>%
  t()

online_choice_2_matrix = hartley_data_for_rl_model %>%
  dplyr::filter(cohort == 'online') %>%
  select(., id, choice_2, trial_num) %>%
  tidyr::spread(., key = id, value = choice_2) %>%
  select(., -trial_num) %>%
  t()

online_reward_matrix = hartley_data_for_rl_model %>%
  dplyr::filter(cohort == 'online') %>%
  select(., id, reward, trial_num) %>%
  tidyr::spread(., key = id, value = reward) %>%
  select(., -trial_num) %>%
  t()

online_missing_matrix = hartley_data_for_rl_model %>%
  dplyr::filter(cohort == 'online') %>%
  select(., id, missing, trial_num) %>%
  tidyr::spread(., key = id, value = missing) %>%
  select(., -trial_num) %>%
  t()

online_choice_1_matrix[is.na(online_choice_1_matrix)] = 1
online_choice_2_matrix[is.na(online_choice_2_matrix)] = 1
online_reward_matrix[is.na(online_reward_matrix)] = 1
online_missing_matrix[is.na(online_missing_matrix)] = 1


save(online_choice_1_matrix, online_missing_matrix, online_reward_matrix, online_choice_2_matrix,
     file = 'clean_data/online_data_for_rl_model.rda')


