# Dominance scope

The only allowed Q5/Q6 dominance transformations are:

| branch | donor move | resulting profile | certified branch |
|---|---|---|---|
| Q5 | 20-point donor | Q3 profile | Q3 Q1--Q4 certificate |
| Q5 | 17-point donor | Q2 profile | Q2 Q1--Q4 certificate |
| Q6 | 19-point donor | Q4 profile | Q4 Q1--Q4 certificate |
| Q6 | 18-point donor | Q3 profile | Q3 Q1--Q4 certificate |

These are profile-size transformations: moving one point from the donor
class to the selected 20-point class changes `(donor, receiver)` by
`(-1,+1)`, then sorting the six sizes gives the listed Q1--Q4 profile. They
were rechecked algebraically against the profile definitions before this
package was made. The package build contains no P6, Q8, Q9, or Q10 branch and
no removed Q10-dominance flag. Any future optional pruning must be audited
and disabled by default.
