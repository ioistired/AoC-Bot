# Unofficial Advent of Code API docs

A private leaderboard is identified by the user ID of the user who owns it. It is a smallish integer (safe to assume 32-bit signed).
A leaderboard invite code has the format: `{leaderboard_id}-{secret_code}`.

## Authentication

Obtain your session cookie by signing in on the website. This session cookie lasts for about 30 days.

## Rate limits

The API should be accessed no more frequently than every 900 seconds (15 minutes).

## Time format

In this document, "Unix time" means the following:

If the time is 0, it is represented as the integer `0`. If the time is non-zero, it is represented
as UTC Unix time, in whole seconds, disregarding leap seconds, as a string.

## Private Leaderboards

```
GET https://adventofcode.com/:event/leaderboard/private/view/:leaderboard_id.json
```

`HEAD` is also supported.

### URL Parameters

| Field            | Type        |
| ---------------- | ----------- |
| `event`          | Decimal int |
| `leaderboard_id` | Decimal int |

Users can only be part of more than one private leaderboard, but can own only one. Each private leaderboard has one owner.
Owner/user IDs also appear to be 32-bit integers.

`event` is a year. Advent of Code has been going on every December since 2015.
Every such year is valid: if nobody has participated in an event that year, the endpoint returns an empty leaderboard.

### Return codes

On invalid session, it returns 302 → /{event}/leaderboard, ie the global leaderboard.
Trying to access a leaderboard you are not a member of returns 302 → /{event}/leaderboard/private.

If your session cookie is correct and you are authorized to view the leaderboard, returns 200 OK along with
a leaderboard object.

### Leaderboard object

| Field              |  Type                                                     |
| ------------------ | --------------------------------------------------------  |
| event              | Four digit decimal string                                 |
| owner_id           | 32-bit integer, as a decimal string                       |
| members            | Mapping of user IDs to [*member objects*](#member-object) |

Each member object listed in the values of the `members` object has joined the requested leaderboard.

### Member object

| Field                | Type                                                                                    |
| -------------------- | --------------------------------------------------------------------------------------- |
| id                   | 32-bit unsigned integer, as a decimal string.                                           |
| name                 | string. If the user is anonymous then `null`.                                           |
| local_score          | 16(?) bit unsigned integer                                                              |
| global_score         | 16(?) bit unsigned integer                                                              |
| stars                | 8 bit unsigned integer                                                                  |
| last_star_ts         | Unix time                                                                               |
| completion_day_level | Mapping of days of the month (1–31) to [*completed day objects*](#completed-day-object) |

`name` is the user's display name. `local_score` and `global_score` are described on the private leaderboard page:
 
- Local Score [*...*] awards users on this leaderboard points much like the global leaderboard.
  If you add or remove users, the points will be recalculated, and the order can change. 
  For N users, the first user to get each star gets N points, the second gets N-1, and the last gets 1.
- Global Score [*...*] uses scores from the global leaderboard. Ties are broken by the user's local score.

`last_star_ts` is the time the user last obtained a star, ie completed one level of one day's challenge.

#### Sample member object

```json
{
  "name": "Io Mintz",
  "id": "214825",
  "stars": 3,
  "completion_day_level": {
    "5": {
      "1": {
        "get_star_ts": "1512282536"
      },
      "2": {
        "get_star_ts": "1513127068"
      }
    },
    "10": {
      "1": {
        "get_star_ts": "1512882378"
      }
    }
  },
  "local_score": 15,
  "last_star_ts": "1513127068",
  "global_score": 0
}
```

### Completed day object

A mapping of levels of that day's challenge (8 bit unsigned integers, as strings) to *completed level objects*.

### Completed level object

| Field               | Type      |
| ------------------- | --------- |
| get_star_ts         | Unix time |

The time this star was obtained.
