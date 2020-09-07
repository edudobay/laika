Feature: Base behavior

  Scenario: Deploy a simple file
    Given the fixture repository
    When on the source dir we run the command: simple-git-deploy deploy main
    And on the deployment dir we run the command: cat hello.txt
    Then we should get status code 0 and the following output
      """
      hello world

      """

  Scenario: Build command fails
    Given the fixture repository
    Given the build command is set to false
    When on the source dir we run the command: simple-git-deploy deploy main
    Then we should get status code 1

  Scenario: Branch does not exist
    Given the fixture repository
    When on the source dir we run the command: simple-git-deploy deploy nonexistent
    Then we should get status code 1

  Scenario: Run post-deploy command
    Given the fixture repository
    Given the post-deploy command is set to touch world.txt
    When on the source dir we run the command: simple-git-deploy deploy main
    And on the deployment dir we run the command: cat world.txt
    Then we should get status code 0 and the following output
      """
      """
