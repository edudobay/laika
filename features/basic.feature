Feature: Base behavior

  Scenario: Deploy a simple file
    Given the fixture repository
    When on the source dir we run the command: laika deploy main
    And on the deployment dir we run the command: cat hello.txt
    Then we should get status code 0 and the following output
      """
      hello world

      """

  Scenario: Build command fails
    Given the fixture repository
    Given the build command is set to false
    When on the source dir we run the command: laika deploy main
    Then we should get status code 1

  Scenario: Branch does not exist on build
    Given the fixture repository
    When on the source dir we run the command: laika build nonexistent
    Then we should get status code 1 and the following error output
      """
      ERROR: Invalid git reference: nonexistent

      """

  Scenario: Branch does not exist on deploy
    Given the fixture repository
    When on the source dir we run the command: laika deploy nonexistent
    Then we should get status code 1 and the following error output
      """
      ERROR: Invalid git reference: nonexistent

      """

  Scenario: Run post-deploy command
    Given the fixture repository
    Given the post-deploy command is set to touch world.txt
    When on the source dir we run the command: laika deploy main
    And on the deployment dir we run the command: cat world.txt
    Then we should get status code 0 and the following output
      """
      """

  Scenario: Run build command with custom shell
    Given the fixture repository
    Given the shell is set to /bin/bash
    Given the build command is set to echo $BASH
    When on the source dir we run the command: laika -q build main
    Then we should get status code 0 and the following output
      """
      /bin/bash

      """
