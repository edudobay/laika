Feature: Base behavior

  Scenario: Deploy a simple change
    Given the fixture repository
    When on the source dir we run the command: simple-git-deploy deploy master
    And on the deployment dir we run the command: cat hello.txt
    Then we should get status code 0 and the following output
      """
      hello world

      """
