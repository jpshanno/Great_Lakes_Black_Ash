#+ Session_Set-up
# .libPaths("E:/R_Libraries")
library(dplyr)
library(ggplot2)
library(lme4)
library(readr)
library(stringr)
library(tidyr)


#+ Load_and_Convert_Sapwood_Areas
sapwoodArea <- 
  read_csv("../../../SapFlux/Data-Raw/Data_Sapwood_Area.csv") %>% 
  mutate_at(.vars = vars(matches("cm$")), 
            .funs = function(x){x/(12*2.54)}) %>% 
  mutate_at(.vars = vars(matches("cm2$")),
            .funs = function(x){x/(12*2.54)^2}) %>% 
  rename_at(.vars = vars(matches("cm")),
            .funs = funs(str_replace,
                         .args = list(pattern = "cm",
                                      replacement = "ft")))

#+ Fit_DBH_to_SA_Model
sapMod <- lm(saparea_ft2 ~ dbh_ft,
                 data = sapwoodArea)

sapwoodArea <- 
  sapwoodArea %>% 
  mutate(fittedValues = predict(sapMod))

ggplot(aes(y = saparea_ft2,
           x = dbh_ft), 
       data = sapwoodArea) +
  geom_point() +
  geom_line(aes(y = fittedValues)) +
  theme_classic()

# Calculate AGB (tons) from DBH (ft)
agb <-  function(DBH.ft){.0327567356 * DBH.ft ^ 2.30399}

inventory <- 
  read_csv("../../../SapFlux/Data-Raw/Data_Overstory_2012.csv") %>% 
  mutate(dbh_ft = dbh_cm/(12*2.54)) %>% 
  select(-dbh_cm)

stocking <- 
  inventory %>% 
  filter(species == "frni") %>% 
  mutate(sapwoodArea_ft2 = as.numeric(predict(sapMod, 
                                   newdata = .)),
         basalArea_ft2 = pi*(dbh_ft/2)^2,
         agb_t = agb(dbh_ft)) %>% 
  group_by(site, plotnum) %>% 
  summarize(trees_n_acre = n()/((pi*37.064^2)/43560),
            dbh_ft = mean(dbh_ft),
            basalArea_ft2_acre = sum(basalArea_ft2)/((pi*37.064^2)/43560),
            sapwoodArea_ft2_acre = sum(sapwoodArea_ft2)/((pi*37.064^2)/43560),
            agb_t_ha = sum(agb_t)/((pi*11.3^2)/10000))

stocking %>% 
  summarize(trees_n_acre = mean(trees_n_acre),
            dbh_ft = mean(dbh_ft),
            basalArea_ft2_acre = mean(basalArea_ft2_acre),
            sapwoodArea_ft2_acre = mean(sapwoodArea_ft2_acre),
            agb_t_ha = mean(agb_t_ha))

stockingMod <- 
  lmer(basalArea_ft2_acre ~ 0 + agb_t_ha + (0 + agb_t_ha|site),
       data = stocking)
fixef(stockingMod)

standSapMod <- 
  lmer(sapwoodArea_ft2_acre ~ basalArea_ft2_acre + (1|site),
       data = stocking)
fixef(standSapMod)

#+ Create Correction factor
# From raster data:
usMean_imp <- 2.5353477283154
caMean_metric <- 0.90934728648167
usMax_imp <- 105.3450012207
caMax_metric <- 23.872190475464


usMean_metric <- usMean_imp/10.31443
usMax_metric <- usMax_imp/10.31443

meansRatio <- usMean_metric/caMean_metric
maxesRatio <- usMax_metric/caMax_metric

adjustmentfactor <- mean(c(meansRatio, maxesRatio))

x <- seq(1, 25, .5)
# BAOld <- 0.0026598*pi/4*(1000/.124785*x)^(2/2.303992)
BANew <-10.31443*(meansRatio * x)
plot(BAOld ~ x)
points(BANew ~ x, col = "red")

ggplot(aes(y = sapwoodArea_ft2_acre,
           x = basalArea_ft2_acre), 
       data = stocking) +
  geom_point() +
  geom_line(aes(y = predict(stockingMod,
                            re.form = ~0)),
            col = "blue") +
  theme_classic()

ggplot(aes(y = basalArea_ft2_acre,
           x = agb_t_ha), 
       data = stocking) +
  geom_point() +
  geom_smooth(method = "lm", 
              formula = "y ~ 0+x",
              span = 1,
              se = F) +
  theme_classic()

flux_ft3_ft2d <- 
  read_csv("../../../Inundation/Output/csv/InunData") %>% 
  filter(Species == "_F. nigra_") %>% 
  mutate(fit = fit * 3.280846) %>% 
  pull(fit)
summary(flux_ft3_ft2d)
  
