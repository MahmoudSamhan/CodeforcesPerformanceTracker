# CodeforcesPerformanceTracker
My first project:
ScoutSystem: A Codeforces performance tracker that fetches real-time data to calculate accuracy and progress. It identifies your top three weaknesses by analyzing submission history across tags and difficulty levels, turning raw data into actionable insights to help you optimize your training and solve smarter.
'''mermaid
classDiagram
    direction BT
    
    class CF_User {
        +String handle
        +String rank
        #Integer rating
        +Profile_Url() String
        +is_active() Boolean
    }

    class Member {
        +List submissions
        +Integer Solve_Count
        +String favorite_tag
        +List weaknesses
        +Datetime last_updated
        +fetch_submissions() void
        +calculate_accuracy() Float
        +analyze_weaknesses() void
    }

    class Problem {
        +Integer contest_id
        +String index
        +String title
        +List tags
        +Float points
        +get_id() String
    }

    class ScoutSystem {
        +String group_name
        +List Members
        +String api_url
        +add_member(handle: String) void
        +generate_report() void
        +export_to_csv(file_name: String) void
    }

    class requests {
        <<interface>>
    }

    Member --|> CF_User : inherits from
    ScoutSystem "1" *-- "*" Member : composition (owns)
    Member "*" -- "*" Problem : interacts with
    ScoutSystem ..> requests : Depends on
    '''
