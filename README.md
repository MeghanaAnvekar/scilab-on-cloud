# Optimisation of Scilab instances on server (May - July2017)
### Contributers - Meghana Anvekar, Divakar Thammishetti and Sumanth Pole

Scilab Textbook Companion (TBC) is one of the flagship activities undertaken by FOSSEE, IIT Bombay. It
aims to port solved examples from standard textbooks using an open source software system, such
as Scilab. It becomes a valuable resource for documentation, function usage search and subject
learning material.

Unlike other scripting languages, Scilab (scilab-adv-cli) loads a huge set of libraries in the
background. Knowing that loading Scilab each time can drastically increase the overhead of code
execution, we optimized the performance of the Scilab instance on cloud by keeping it alive in
the background.The code from different users is processed by a group of Scilab instances running
in parallel, in order to reduce the response time (by 50%) in sending back the result.

