# Load libraries
library(ggplot2) # plotting
library(gganimate) # animations
library(gifski) 
library(dplyr) # %>% operator
library(png)
library(ggflags) # flags!
library(countrycode) # country codes
library(wesanderson) # color palettes

# Load maternal mortality data
df <- read.csv('Projects/Maternal Mortality/oecd_mmr.csv')

# Filter data by G7 countries
g7_countries <-  c("Canada", "France", "Germany", "Italy", "Japan", "United Kingdom", "United States")
df <- df %>% filter(Country %in% g7_countries)
                      
# Get flag codes
df$Flag <- tolower(countrycode(df$Code, origin="iso3c", destination="iso2c"))

# Get text labels
df <- df %>% mutate(Text = case_when(Year==2017 ~ as.character(Maternal.Mortality.Ratio), Year!=2017 ~ ""))

# Make animated plot
p <- df %>%
  arrange(Year) %>% # Order df by Year (This is important for the flag icons!)
  ggplot(aes(x=Year, y=Maternal.Mortality.Ratio, group=Country, country=Flag, color=Country)) +
  scale_color_manual(values=c("#3B9AB2", "#63ADBE", "#9EBE91", "#8C8C8C", "#E4B80E", "#E67D00", "#F21A00")) + # Set line colors
  geom_text(aes(x=Year+1.5, label=Text), hjust=0.5, vjust=0.25, size=6, color="gray30") + # Text labels
  scale_x_continuous(limits=c(2000, 2018.5)) + scale_y_continuous(expand=c(0, 0), limits=c(0, 20)) + # Set x- and y-axis limits
  labs(title = 'Maternal Mortality Ratios (per 100,000 births) in the G7', 
       y = 'Maternal Mortality Ratio',
       caption = 'Source: World Health Organization OData API') + 
  geom_line(size=1.5) + # Make a line plot
  geom_flag(size=15) + scale_country() + # Add flag icons
  transition_reveal(Year) + 
  theme_classic() +
  theme(plot.margin = margin(10, 10, 10, 5.5),
        plot.title = element_text(size = 18), # Set plot title text size
        axis.title  = element_text(size=15), # Set x- and y-axis title text size
        axis.text = element_text(size=15), # Set x- and y-axis label text size
        plot.caption =  element_text(size=14, color="grey45")) + # Set caption text size and caption position  
  guides(country=F, color=F) # Hide legend
animate(p, end_pause=45, fps=200, height=375, width=500) 

# Save animated plot
#anim_save(file="Projects/Maternal Mortality/mex.gif")

anim_save(file="Projects/Maternal Mortality/mmr-final-g7.mp4")


