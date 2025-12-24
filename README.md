# ufa-scraper
Web Scraper & ELO Ranker for UFA statistics

TODO:
- need to implement elo ranker
- need to figure out how i want to store data (currently csv files)
- how can i make this scraping more efficient?
- what are best practices for splitting scraping jobs?
- tbd...

Event Types
| `t`    | **Meaning**                               | 
| ------ | ----------------------------------------- | 
| **50** | Start-of-game                             | 
| **1**  | O-line set                                | 
| **2**  | D Line set                                | 
| **3**  | Pull event                                | 
| **4**  | Out of bounds pull                        | 
| **5**  | Block                                     | 
| **6**  | Callahan                                  | 
| **8**  | Throwaway                                 | 
| **9**  | Throwaway caused                          | 
| **11** | Stoppage / foul / pick                    | 
| **12** | The restart / check event                 | 
| **13** | Neutral dead disc marker                  | 
| **14** | Timeout                                   | 
| **17** | Stall                                     | 
| **19** | Dropped pass                              | 
| **20** | Throw attempt                             | 
| **21** | Indicates other team scored               | 
| **22** | Goal                                      |  
| **40** | Line change                               | 
| **41** | Line change                               |  
| **44** | We're offsides                            | 
| **45** | They're offsides                          |

| Field    | Meaning                             | Notes                                                            |
| -------- | ----------------------------------- | ---------------------------------------------------------------- |
| **r**    | *Roster ID of the player involved*  | Used for throws, catches, blocks.                                |
| **l**    | *List of roster IDs*                | The 7 players in the point/line.                                 |
| **s**    | *Scorer roster ID*                  | Appears in goal‐related events (t=42, t=54).                     |
| **x, y** | *Field coordinates*                 | Normalized: 0 = center, ±something = left/right, 100 = end zone. |
| **n**    | *Event number / timestamp-ish*      | Internal ordering number; not meaningful for stats.              |
| **ms**   | *Milliseconds since sequence start* | Only appears in pull events.                                     |
