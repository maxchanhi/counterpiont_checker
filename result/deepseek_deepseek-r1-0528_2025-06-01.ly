\version "2.24.4"
\header {
  title = "First Species Counterpoint Composed by LLM"
  subtitle = "Generated by deepseek/deepseek-r1-0528 on 2025-06-01 (Successful Output)"
}

\score {
  <<
    \new Staff = "Counterpoint" <<
      \clef treble
      \key c \major
      \time 4/4
      \fixed c' { 
        c'1 | b1 | a1 | b1 | a1 | b1 | c'1 | d'1 | g1 | a1 | c'1
      }
    >>
    \new Staff = "CantusFirmus" <<
      \clef treble
      \key c \major
      \time 4/4
      \fixed c' { 
        c1 | d1 | f1 | e1 | f1 | g1 | a1 | g1 | e1 | d1 | c1
      }
    >>
  >>
  \layout { }
  \midi { \tempo 1 = 80 }
}
