#!/bin/sh

doconce format html slides1 SLIDE_TYPE=dummy SLIDE_THEME=dummy
doconce slides_html slides1 doconce

doconce format html slides1 --pygments_html_style=default --keep_pygments_html_bg SLIDE_TYPE=html SLIDE_THEME=blueish --html_style=blueish --html_output=slides1_html_blueish
doconce split_html slides1_html_blueish --method=colorline  # one long file

doconce format html slides1 --pygments_html_style=default --keep_pygments_html_bg SLIDE_TYPE=html SLIDE_THEME=bloodish --html_style=bloodish --html_output=slides1_html_bloodish
doconce split_html slides1_html_bloodish --method=space8  # one long file

doconce format html slides1 SLIDE_TYPE=html SLIDE_THEME=solarized --html_style=solarized --html_output=slides1_html_solarized
doconce slides_html slides1_html_solarized doconce --nav_button=gray2,bottom --font_size=slides

doconce format html slides1 SLIDE_TYPE=html SLIDE_THEME=solarized2 --html_style=solarized2 --html_output=slides1_html_solarized2
doconce slides_html slides1_html_solarized2 doconce --nav_button=gray2,bottom --font_size=slides

doconce format html slides1 SLIDE_TYPE=html SLIDE_THEME=solarized3 --html_style=solarized3 --html_output=slides1_html_solarized3
doconce slides_html slides1_html_solarized3 doconce --nav_button=gray2,bottom --font_size=slides

doconce format html slides1 SLIDE_TYPE=html SLIDE_THEME=solarized3 --html_style=solarized3 --html_output=slides1_html_solarized3_space
doconce split_html slides1_html_solarized3_space --method=space10

doconce format html slides1 SLIDE_TYPE=html SLIDE_THEME=solarized3_dark --html_style=solarized3_dark --html_output=slides1_html_solarized3_dark
doconce slides_html slides1_html_solarized3_dark doconce --nav_button=gray2,bottom --font_size=slides

doconce format html slides1 --pygments_html_style=fruity --keep_pygments_html_bg SLIDE_TYPE=deck SLIDE_THEME=neon
doconce slides_html slides1 deck --html_slide_theme=neon
cp slides1.html slides1_deck_neon.html

doconce format html slides1 --pygments_html_style=fruity --keep_pygments_html_bg SLIDE_TYPE=deck SLIDE_THEME=sandstone.aurora
doconce slides_html slides1 deck --html_slide_theme=sandstone.aurora
cp slides1.html slides1_deck_sandstone_aurora.html

doconce format html slides1 --pygments_html_style=native --keep_pygments_html_bg SLIDE_TYPE=deck SLIDE_THEME=sandstone.dark
doconce slides_html slides1 deck --html_slide_theme=sandstone.dark
cp slides1.html slides1_deck_sandstone_dark.html

doconce format html slides1 --pygments_html_style=fruity --keep_pygments_html_bg SLIDE_TYPE=deck SLIDE_THEME=sandstone.mdn
doconce slides_html slides1 deck --html_slide_theme=sandstone.mdn
cp slides1.html slides1_deck_sandstone_mdn.html

doconce format html slides1 --pygments_html_style=default --keep_pygments_html_bg SLIDE_TYPE=deck SLIDE_THEME=sandstone.mightly
doconce slides_html slides1 deck --html_slide_theme=sandstone.mightly
cp slides1.html slides1_deck_sandstone_mightly.html

doconce format html slides1 --pygments_html_style=autumn --keep_pygments_html_bg SLIDE_TYPE=deck SLIDE_THEME=beamer
doconce slides_html slides1 deck --html_slide_theme=beamer
cp slides1.html slides1_deck_beamer.html

doconce format html slides1 --pygments_html_style=default --keep_pygments_html_bg SLIDE_TYPE=deck SLIDE_THEME=mnml
doconce slides_html slides1 deck --html_slide_theme=mnml
cp slides1.html slides1_deck_mnml.html

doconce format html slides1 --pygments_html_style=default --keep_pygments_html_bg SLIDE_TYPE=deck SLIDE_THEME=sandstone.firefox
doconce slides_html slides1 deck --html_slide_theme=sandstone.firefox
cp slides1.html slides1_deck_sandstone_firefox.html

doconce format html slides1 --pygments_html_style=perldoc --keep_pygments_html_bg SLIDE_TYPE=deck SLIDE_THEME=sandstone.default
doconce slides_html slides1 deck --html_slide_theme=sandstone.default
cp slides1.html slides1_deck_sandstone_default.html

doconce format html slides1 --pygments_html_style=emacs --keep_pygments_html_bg SLIDE_TYPE=deck SLIDE_THEME=sandstone.light
doconce slides_html slides1 deck --html_slide_theme=sandstone.light
cp slides1.html slides1_deck_sandstone_light.html

doconce format html slides1 --pygments_html_style=autumn --keep_pygments_html_bg SLIDE_TYPE=deck SLIDE_THEME=swiss
doconce slides_html slides1 deck --html_slide_theme=swiss
cp slides1.html slides1_deck_swiss.html

doconce format html slides1 --pygments_html_style=autumn --keep_pygments_html_bg SLIDE_TYPE=deck SLIDE_THEME=web-2.0
doconce slides_html slides1 deck --html_slide_theme=web-2.0
cp slides1.html slides1_deck_web-2_0.html

doconce format html slides1 --pygments_html_style=default --keep_pygments_html_bg SLIDE_TYPE=deck SLIDE_THEME=cbc
doconce slides_html slides1 deck --html_slide_theme=cbc
cp slides1.html slides1_deck_cbc.html

doconce format html slides1 --pygments_html_style=perldoc --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=beige
doconce slides_html slides1 reveal --html_slide_theme=beige
cp slides1.html slides1_reveal_beige.html

doconce format html slides1 --pygments_html_style=perldoc --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=beigesmall
doconce slides_html slides1 reveal --html_slide_theme=beigesmall
cp slides1.html slides1_reveal_beigesmall.html

doconce format html slides1 --pygments_html_style=perldoc --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=solarized
doconce slides_html slides1 reveal --html_slide_theme=solarized
cp slides1.html slides1_reveal_solarized.html

doconce format html slides1 --pygments_html_style=perldoc --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=serif
doconce slides_html slides1 reveal --html_slide_theme=serif
cp slides1.html slides1_reveal_serif.html

doconce format html slides1 --pygments_html_style=autumn --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=simple
doconce slides_html slides1 reveal --html_slide_theme=simple
cp slides1.html slides1_reveal_simple.html

doconce format html slides1 --pygments_html_style=autumn --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=white
doconce slides_html slides1 reveal --html_slide_theme=white
cp slides1.html slides1_reveal_white.html

doconce format html slides1 --pygments_html_style=monokai --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=blood
doconce slides_html slides1 reveal --html_slide_theme=blood
cp slides1.html slides1_reveal_blood.html

doconce format html slides1 --pygments_html_style=monokai --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=black
doconce slides_html slides1 reveal --html_slide_theme=black
cp slides1.html slides1_reveal_black.html

doconce format html slides1 --pygments_html_style=default --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=sky
doconce slides_html slides1 reveal --html_slide_theme=sky
cp slides1.html slides1_reveal_sky.html

doconce format html slides1 --pygments_html_style=fruity --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=moon
doconce slides_html slides1 reveal --html_slide_theme=moon
cp slides1.html slides1_reveal_moon.html

doconce format html slides1 --pygments_html_style=fruity --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=night
doconce slides_html slides1 reveal --html_slide_theme=night
cp slides1.html slides1_reveal_night.html

doconce format html slides1 --pygments_html_style=native --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=darkgray
doconce slides_html slides1 reveal --html_slide_theme=darkgray
cp slides1.html slides1_reveal_darkgray.html

doconce format html slides1 --pygments_html_style=native --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=league
doconce slides_html slides1 reveal --html_slide_theme=league
cp slides1.html slides1_reveal_league.html

doconce format html slides1 --pygments_html_style=default --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=cbc
doconce slides_html slides1 reveal --html_slide_theme=cbc
cp slides1.html slides1_reveal_cbc.html

doconce format html slides1 --pygments_html_style=autumn --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=simula
doconce slides_html slides1 reveal --html_slide_theme=simula
cp slides1.html slides1_reveal_simula.html

doconce format html slides1 --pygments_html_style=monokai --keep_pygments_html_bg SLIDE_TYPE=csss SLIDE_THEME=csss_default
doconce slides_html slides1 csss --html_slide_theme=csss_default
cp slides1.html slides1_csss_csss_default.html

doconce format html slides1 --pygments_html_style=autumn --keep_pygments_html_bg SLIDE_TYPE=dzslides SLIDE_THEME=dzslides_default
doconce slides_html slides1 dzslides --html_slide_theme=dzslides_default
cp slides1.html slides1_dzslides_dzslides_default.html

doconce format html slides1 --pygments_html_style=autumn --keep_pygments_html_bg SLIDE_TYPE=html5slides SLIDE_THEME=template-default
doconce slides_html slides1 html5slides --html_slide_theme=template-default
cp slides1.html slides1_html5slides_template-default.html

doconce format html slides1 --pygments_html_style=autumn --keep_pygments_html_bg SLIDE_TYPE=html5slides SLIDE_THEME=template-io2011
doconce slides_html slides1 html5slides --html_slide_theme=template-io2011
cp slides1.html slides1_html5slides_template-io2011.html

doconce format html slides1 --pygments_html_style=autumn --keep_pygments_html_bg SLIDE_TYPE=remark SLIDE_THEME=light
doconce slides_html slides1 remark --html_slide_theme=light
cp slides1.html slides1_remark_light.html

doconce format html slides1 --pygments_html_style=native --keep_pygments_html_bg SLIDE_TYPE=remark SLIDE_THEME=dark
doconce slides_html slides1 remark --html_slide_theme=dark
cp slides1.html slides1_remark_dark.html

echo "Here are the slide shows:"
/bin/ls slides1_*_*.html
