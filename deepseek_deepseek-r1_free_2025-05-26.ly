\version "2.24.4"
\header {
  title = "First Species Counterpoint Example"
  subtitle = "Generated from MIDI Notes"
}

\score {
  <<
    \new Staff = "Counterpoint" <<
      \clef treble
      \key c \major
      \time 4/4
      \fixed c' { 
        gis'1 | ais'1 | ais'1 | ais'1 | cis'1 | dis'1 | c''1 | ais'1 | gis'1 | e'1 | gis'1
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
