# Human_or_Robot

![](https://niccollsanddimes.files.wordpress.com/2015/06/robot-woman-office.jpg)

## Description
Ever wonder what it's like to work at Facebook? Facebook and Kaggle are launching an Engineering competition for 2015. Trail blaze your way to the top of the leader board to earn an opportunity at interviewing for a role as a software engineer, working on world class Machine Learning problems. 

In this competition, you'll be chasing down robots for an online auction site. Human bidders on the site are becoming increasingly frustrated with their inability to win auctions vs. their software-controlled counterparts. As a result, usage from the site's core customer base is plummeting.

In order to rebuild customer happiness, the site owners need to eliminate computer generated bidding from their auctions. Their attempt at building a model to identify these bids using behavioral data, including bid frequency over short periods of time, has proven insufficient. 

The goal of this competition is to identify online auction bids that are placed by "robots", helping the site owners easily flag these users for removal from their site to prevent unfair auction activity. 

## Results

model | Public LB | Private LB | Date | Commit
--- | --- | --- | --- | ---
Bid number statistical analysis and Xgboost classifier | 0.89928 | 0.90050 | 9th January 2018 | 6f91faf0eab2ad50fc54c1dd31cdce467f5ecdaa
Bid number and bid time statistical analysis and Xgboost classifier | 0.88477 | 0.91041 | 10th January 2018 | e4a71983938b7500ef65a1d404219d7d0fd36375
Bid number and bid time statistical analysis and Xgboost classifier (optimization) | 0.88546 | 0.91498 | 10th January 2018 | 8f1ab154e3321f929225358a50a74f5e9b4c3940
Bid number, bid argmax and bid time statistical analysis (normalize continuous data) and Xgboost classifier  | 0.91249 | 0.92072 | 14th January 2018 | 618842a9a2721155bbc3290b35afb45a1b96fe7f
--- | --- | --- | --- | ---
