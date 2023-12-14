library(rstan)
library(loo)
library(tidyverse)

# Function to calculate ELPD differences between LOO objects with a chosen reference
# Rewrite of the loo_compare() function 
get_loo_compare_manual = function(reference_loo, compare_loo_list){
  # number of log likelihood estimates to compute over
  n = nrow(reference_loo$pointwise)
  
  for (i in 1:length(compare_loo_list)){
      m2 = compare_loo_list[[i]]
      # sum differences in pointwise log likelihood
      elpd_diff = sum(reference_loo$pointwise[,1] - m2$pointwise[,1])
      # se of differences in pointwise log likelihood
      elpd_se = sd(reference_loo$pointwise[,1] - m2$pointwise[,1])*sqrt(n)

      # put together output data in a dataframe
      comp = data.frame(elpd_diff=elpd_diff, elpd_se = elpd_se)
      comp$model=names(compare_loo_list[i])
      if (i ==1){
        outdata = comp
      }else{
        outdata = rbind(outdata, comp)
      }
  }
  return(outdata)
}

# Import LOO results
load('../results/online_model_comparison.rda')
load('../results/danl_model_comparison.rda')
load('../results/decker_model_comparison.rda')
load('../results/potter_model_comparison.rda')

# Run LOO model comparison for each cohort
online_comparison = get_loo_compare_manual(reference_loo = loo_mbmf_only_online, 
                       compare_loo_list = list('MB-MF+SM1'=loo_mbmf_spatiomotor_online, 
                                               'MB-MF+SM2'=loo_mbmf_spatiomotor2_online,
                                               'SM2'=loo_spatiomotor_only_online)) %>%
  mutate(cohort = 'Nussenbaum')

danl_comparison = get_loo_compare_manual(reference_loo = loo_mbmf_only_danl, 
                       compare_loo_list = list('MB-MF+SM1'=loo_mbmf_spatiomotor_danl, 
                                               'MB-MF+SM2'=loo_mbmf_spatiomotor2_danl,
                                               'SM2'=loo_spatiomotor_only_danl)) %>%
  mutate(cohort = 'PACCT')

decker_comparison = get_loo_compare_manual(reference_loo = loo_mbmf_only_decker, 
                       compare_loo_list = list('MB-MF+SM1'=loo_mbmf_spatiomotor_decker, 
                                               'MB-MF+SM2'=loo_mbmf_spatiomotor2_decker,
                                               'SM2'=loo_spatiomotor_only_decker)) %>%
  mutate(cohort = 'Decker')

potter_comparison = get_loo_compare_manual(reference_loo = loo_mbmf_only_potter, 
                       compare_loo_list = list('MB-MF+SM1'=loo_mbmf_spatiomotor_potter, 
                                               'MB-MF+SM2'=loo_mbmf_spatiomotor2_potter,
                                               'SM2'=loo_spatiomotor_only_potter)) %>%
  mutate(cohort = 'Potter')

# Combine & Calculate Approx 95% CI
all_comparisons = rbind(danl_comparison, decker_comparison, potter_comparison, online_comparison)


all_comparisons = all_comparisons %>%
  mutate(elpd_diff_lwr = elpd_diff - 2*elpd_se, 
         elpd_diff_upr = elpd_diff + 2*elpd_se)

# Make plot & save
comparison_plot = ggplot(all_comparisons, aes(x = cohort, y = elpd_diff, color = model)) +
  geom_point(position = position_dodge(0.2)) +
  geom_errorbar(aes(ymin = elpd_diff_lwr, ymax = elpd_diff_upr), width= 0, position = position_dodge(0.2)) +
  geom_hline(yintercept = 0, lty = 2) +
  theme_bw() +
  labs(y = 'LOO ELPD Difference vs. MB-MF Only')

save(all_comparisons, comparison_plot, file='../results/comparison_plot.rda')
ggsave(comparison_plot, filename='../results/comparison_plot.png', height = 5, width=8)