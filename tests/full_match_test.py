import unittest
import json
import matcher
import os
from params import Params
from TestUtil import TestUtil

# Instructions for running this test case with pytest
# go into the virtual environment for running the matcher
# cd openreview-matcher
# source venv/bin/activate
# cd tests
# export PYTHONPATH='.:..'    // tells pytest to search for python files in this dir and the one above
# pytest -s full_match_test.py  // runs pytest without capturing output into temp.py



def json_of_response(response):
    """Decode json from response"""
    return json.loads(response.data.decode('utf8'))




class FullMatchTest(unittest.TestCase):

    # called once at beginning of suite
    @classmethod
    def setUpClass(cls):
        cls.flask_app_test_client = matcher.app.test_client()
        cls.flask_app_test_client.testing = True


    @classmethod
    def tearDownClass(cls):
        pass

    # called at the beginning of each test
    # This uses the test_client() which builds the Flask app and runs it for testing.  It does not
    # start it in such a way that the app initializes correctly (i.e. by calling matcher/app.py) so
    # we have to set a couple things correctly
    def setUp (self):
        # self.app = matcher.app.test_client()
        # self.app.testing = True
        # self.app = FullMatchTest.flask_app_test_client

        # Sets the webapp up so that it will switch to using the mock OR client
        # matcher.app.testing = True
        # Turn off logging in the web app so that tests run with a clean console
        matcher.app.logger.disabled = True
        matcher.app.logger.parent.disabled = True
        or_baseurl = os.getenv('OPENREVIEW_BASEURL')
        assert or_baseurl != None and or_baseurl != ''
        matcher.app.config['OPENREVIEW_BASEURL'] = or_baseurl
        # only need one TestUtil object for all tests
        or_baseurl = os.getenv('OPENREVIEW_BASEURL')
        self.tu = TestUtil.get_instance(or_baseurl, FullMatchTest.flask_app_test_client)
        print('-'*60)


    def tearDown (self):
        pass




    # To look at the results of test1:
    # http://openreview.localhost/assignments?venue=FakeConferenceForTesting1.cc/2019/Conference
    # To login to OR when running test suite:  OpenReview.net / 1234 (as defined in get_client above)

    # @unittest.skip
    def test1_10papers_7reviewers (self):
        '''
        Tests 10 papers each requiring 1 review.  7 users each capable of giving 2 reviews.
        Expects:  produce an assignment
        '''
        params = Params({Params.NUM_PAPERS: 10,
                  Params.NUM_REVIEWERS: 7,
                  Params.NUM_REVIEWS_NEEDED_PER_PAPER: 1,
                  Params.REVIEWER_MAX_PAPERS: 2,
            })
        self.tu.set_and_print_test_params(params)
        try:
            self.tu.test_matcher()
            self.tu.check_completed_match()
        except Exception as exc:
            self.show_test_exception(exc)

    # @unittest.skip
    def test2_10papers_7reviewers_5cust_load_5shortfall (self):
        '''
        Tests 10 papers each requiring 2 reviews.  7 users each capable of giving 3 reviews.  Custom_loads will reduce supply by 5
        Expects:  Failure because supply (16) < demand (20)
        '''
        params = Params({Params.NUM_PAPERS: 10,
                  Params.NUM_REVIEWERS: 7,
                  Params.NUM_REVIEWS_NEEDED_PER_PAPER: 2,
                  Params.REVIEWER_MAX_PAPERS: 3,
                  Params.CUSTOM_LOAD_CONFIG: {Params.CUSTOM_LOAD_SUPPLY_DEDUCTION: 5}
            })
        self.tu.set_and_print_test_params(params)
        try:
            self.tu.test_matcher()
            self.tu.check_match_error("Because actual supply {} < demand {}".format(params.actual_supply, params.demand))
        except Exception as exc:
                self.show_test_exception(exc)

    # @unittest.skip
    def test3_10papers_7reviewers_0cust_load (self):
        '''
        Tests 10 papers each requiring 2 reviews.  7 users each capable of giving 3 reviews.  Custom_loads will reduce supply by 0
        Expects:  Successful production of assignment
        '''
        params = Params({Params.NUM_PAPERS: 10,
                  Params.NUM_REVIEWERS: 7,
                  Params.NUM_REVIEWS_NEEDED_PER_PAPER: 2,
                  Params.REVIEWER_MAX_PAPERS: 3,
                  Params.CUSTOM_LOAD_CONFIG: {Params.CUSTOM_LOAD_SUPPLY_DEDUCTION: 0}
            })
        self.tu.set_and_print_test_params(params)
        try:
            self.tu.test_matcher()
            self.tu.check_completed_match()
        except Exception as exc:
            self.show_test_exception(exc)

    # @unittest.skip
    def test4_10papers_7reviewers_5cust_load_excess (self):
        '''
        Tests 10 papers each requiring 2 reviews.  7 users each capable of giving 4 reviews.  Custom_loads will reduce supply by 5
        Expects:  Successful production of assignment
        '''
        params = Params({Params.NUM_PAPERS: 10,
                  Params.NUM_REVIEWERS: 7,
                  Params.NUM_REVIEWS_NEEDED_PER_PAPER: 2,
                  Params.REVIEWER_MAX_PAPERS: 4,
                  Params.CUSTOM_LOAD_CONFIG: {Params.CUSTOM_LOAD_SUPPLY_DEDUCTION: 5}
            })
        self.tu.set_and_print_test_params(params)
        try:
            self.tu.test_matcher()
            self.tu.check_completed_match()

        except Exception as exc:
            self.show_test_exception(exc)

    # @unittest.skip
    def test5_10papers_7reviewers_4locks (self):
        '''
        Tests 10 papers each requiring 2 reviews.  7 users each capable of giving 4 reviews.  Constraints lock in users to 4 papers
        Expects:  Successful production of assignment where locked user are assigned to the papers they are locked to.
        '''
        params = Params({Params.NUM_PAPERS: 10,
                  Params.NUM_REVIEWERS: 7,
                  Params.NUM_REVIEWS_NEEDED_PER_PAPER: 2,
                  Params.REVIEWER_MAX_PAPERS: 4,
                  # paper indices mapped to reviewer indices to indicate lock of the pair
                  Params.CONSTRAINTS_CONFIG: {
                      Params.CONSTRAINTS_LOCKS: {0: [4], 2: [4], 4: [1], 5: [1]}
                  }
            })
        self.tu.set_and_print_test_params(params)
        try:
            self.tu.test_matcher()
            self.tu.check_completed_match(check_constraints=True)

        except Exception as exc:
            self.show_test_exception(exc)

    @unittest.skip
    def test6_10papers_7reviewers_8vetos (self):
        '''
        Tests 10 papers each requiring 2 reviews.  7 users each capable of giving 4 reviews.  Constraints veto users in 4 papers
        Expects:  Successful production of assignment where vetoed users do are not assigned to papers they were vetoed from.
        '''
        params = Params({Params.NUM_PAPERS: 10,
                  Params.NUM_REVIEWERS: 7,
                  Params.NUM_REVIEWS_NEEDED_PER_PAPER: 2,
                  Params.REVIEWER_MAX_PAPERS: 4,
                  # paper indices mapped to reviewer indices to indicate veto of the pair
                  Params.CONSTRAINTS_CONFIG: {
                      Params.CONSTRAINTS_VETOS : {0: [1,2], 1: [1,2], 2: [1,2,3], 3: [5]}
                  }
            })
        self.tu.set_and_print_test_params(params)
        try:
            self.tu.test_matcher()
            self.tu.check_completed_match(check_constraints=True)

        except Exception as exc:
            self.show_test_exception(exc)

    @unittest.skip
    def test7_10papers_7reviewers_3vetos (self):
        '''
        Tests 10 papers each requiring 2 reviews.  7 users each capable of giving 4 reviews.  Constraints veto users in 3 papers
        Expects:  Successful production of assignment where vetoed users do are not assigned to papers they were vetoed from.
        '''
        params = Params({Params.NUM_PAPERS: 10,
                  Params.NUM_REVIEWERS: 7,
                  Params.NUM_REVIEWS_NEEDED_PER_PAPER: 2,
                  Params.REVIEWER_MAX_PAPERS: 4,
                  # paper indices mapped to reviewer indices to indicate veto of the pair
                  Params.CONSTRAINTS_CONFIG: {
                      Params.CONSTRAINTS_VETOS : {0: [0], 1: [1], 2: [2]}
                  }
            })
        self.tu.set_and_print_test_params(params)
        try:
            self.tu.test_matcher()
            self.tu.check_completed_match(check_constraints=True)

        except Exception as exc:
            self.show_test_exception(exc)

    # @unittest.skip
    def test8_10papers_7reviewers_3locks (self):
        '''
        Tests 10 papers each requiring 2 reviews.  7 users each capable of giving 4 reviews.  Constraints lock users in 2 papers
        Expects:  Successful production of assignment where locked users are assigned to papers they were locked to.
        '''
        params = Params({Params.NUM_PAPERS: 10,
                  Params.NUM_REVIEWERS: 7,
                  Params.NUM_REVIEWS_NEEDED_PER_PAPER: 2,
                  Params.REVIEWER_MAX_PAPERS: 4,
                  # paper indices mapped to reviewer indices to indicate lock of the pair
                  Params.CONSTRAINTS_CONFIG: {
                      Params.CONSTRAINTS_LOCKS : {0: [0], 1: [1,2]}
                  }
            })
        self.tu.set_and_print_test_params(params)
        try:
            self.tu.test_matcher()
            self.tu.check_completed_match(check_constraints=True)

        except Exception as exc:
            self.show_test_exception(exc)


    @unittest.skip
    def test9_10papers_7reviewers_10locks (self):
        '''
        Tests 10 papers each requiring 2 reviews.  7 users each capable of giving 4 reviews.  Constraints lock users in all 10 papers
        Expects:  Successful production of assignment where locked users are assigned to papers they were locked to.
        '''
        params = Params({Params.NUM_PAPERS: 10,
                  Params.NUM_REVIEWERS: 7,
                  Params.NUM_REVIEWS_NEEDED_PER_PAPER: 2,
                  Params.REVIEWER_MAX_PAPERS: 4,
                  # paper indices mapped to reviewer indices to indicate lock of the pair
                  Params.CONSTRAINTS_CONFIG: {
                      Params.CONSTRAINTS_LOCKS : {0:[0], 1:[1], 2:[2], 3:[3], 4:[4], 5:[5], 6:[6], 7:[0], 8:[1], 9:[2]}
                  }
            })
        self.tu.set_and_print_test_params(params)
        try:
            self.tu.test_matcher()
            self.tu.check_completed_match(check_constraints=True)

        except Exception as exc:
            self.show_test_exception(exc)


    @unittest.skip
    def test10_10papers_7reviewers_4vetos_8locks (self):
        '''
        Tests 10 papers each requiring 2 reviews.  7 users each capable of giving 4 reviews.  Constraints veto users in 4 papers and lock users in 4 papers
        Expects:  Successful production of assignment where locked users are assigned to papers they were locked to and vetoed users are not assigned to papers they were vetoed from.
        '''
        params = Params({Params.NUM_PAPERS: 10,
                  Params.NUM_REVIEWERS: 7,
                  Params.NUM_REVIEWS_NEEDED_PER_PAPER: 2,
                  Params.REVIEWER_MAX_PAPERS: 4,
                  Params.CONSTRAINTS_CONFIG: {
                      Params.CONSTRAINTS_VETOS : {0: [1,2], 1: [1,2], 2: [1,2,3], 3: [5]},
                      Params.CONSTRAINTS_LOCKS: {0: [4], 2: [4], 4: [1], 5: [1]}
                  }
            })
        self.tu.set_and_print_test_params(params)
        try:
            self.tu.test_matcher()
            self.tu.check_completed_match(check_constraints=False)

        except Exception as exc:
            self.show_test_exception(exc)
        finally:
            pass

    # @unittest.skip
    def test11_5papers_4reviewers_conflicts (self):
        '''
        Tests 5 papers each requiring 2 reviews.  4 users each capable of giving 3 reviews.  6 conflicts are created between papers/reviewers.
        Expects: Not sure if this should fail because of the number of conflicts limiting the supply significantly.
        '''
        params = Params({Params.NUM_PAPERS: 5,
                  Params.NUM_REVIEWERS: 4,
                  Params.NUM_REVIEWS_NEEDED_PER_PAPER: 2,
                  Params.REVIEWER_MAX_PAPERS: 3,
                  Params.CONFLICTS_CONFIG : {0: [1,2], 1: [1,2], 3: [3], 4: [3]}
            })
        self.tu.set_and_print_test_params(params)
        try:
            self.tu.test_matcher()
            self.tu.check_completed_match(check_constraints=False)

        except Exception as exc:
            self.show_test_exception(exc)



    def show_test_exception (self, exc):
        print("Something went wrong while running this test")
        print(exc)
        raise exc

'''
    def test4_10papers_7reviewers_5cust_loads (self):
        test_num = 4
        if not self._should_run(test_num):
            return
        num_papers = 10
        num_reviewers = 7
        reviews_needed_per_paper = 2
        reviewer_max_papers = 4
        custom_load_percentage = 0.05
        print("\n\nTesting with {} papers, {} reviewers. \nEach paper needs at least {} review(s).  \nEach reviewer must review {} paper(s). \n{}% of reviewers have a custom_load below the min number of papers of reviewer should review".
              format(num_papers, num_reviewers,reviews_needed_per_paper,reviewer_max_papers, custom_load_percentage*100))
        try:
            self._test_matcher(test_num, num_papers, num_reviewers, paper_min_reviewers=reviews_needed_per_paper, reviewer_max_papers=reviewer_max_papers,
                               custom_load_percentage=custom_load_percentage*100)
            config_stat = self.get_config_status(self.conf.config_note_id)
            review_supply = self.conf.get_total_review_supply()
            if review_supply < num_papers * reviews_needed_per_paper:
                print("Expecting error because review supply", review_supply, "< demand", num_papers * reviews_needed_per_paper)
                assert config_stat == Configuration.STATUS_ERROR, "Failure: Config status is {} expected {}".format(config_stat, Configuration.STATUS_ERROR)
            else:
                print("Expecting success because review supply", review_supply, ">= demand", num_papers * reviews_needed_per_paper)
                assert config_stat == Configuration.STATUS_COMPLETE, "Failure: Config status is {} expected {}".format(config_stat, Configuration.STATUS_NO_SOLUTION)
        except Exception as exc:
            print("Something went wrong while running this test")
            print(exc)
            print('-------------------')
            raise exc
        finally:
            pass

    # def test3_10papers_7reviewers_25cust_loads (self):
    #     if not self._should_run(3):
    #         return
    #     print("Testing with 10 papers, 7 reviewers, 25% custom loads")
    #     self._test_matcher(3, 10, 7, conflict_percentage = 0, paper_min_reviewers = 2, reviewer_max_papers = 3, custom_load_percentage = 0.25)
    #     config_stat = self.conf.get_config_note_status()
    #     assert config_stat == Configuration.STATUS_COMPLETE, "Failure: Config status is {} expected {}".format(config_stat, Configuration.STATUS_NO_SOLUTION)
    #     num_assign_notes = self.conf.get_num_assignment_notes()
    #     assert num_assign_notes == self.num_papers, "Number of assignments {} is not same as number of papers {}".format(num_assign_notes, self.num_papers)
    #
    # def test4_10papers_7reviewers_75conflicts (self):
    #     if not self._should_run(4):
    #         return
    #     print("Testing with 10 papers, 7 reviewers 75% conflicts")
    #     self._test_matcher(4, 10, 7, conflict_percentage = 0.75, paper_min_reviewers = 2, reviewer_max_papers = 3)
    #     config_stat = self.conf.get_config_note_status()
    #     assert config_stat == Configuration.STATUS_NO_SOLUTION, "Failure: Config status is {}".format(config_stat)
    #
    # def test5_10papers_7reviewers_25conflicts (self):
    #     if not self._should_run(5):
    #         return
    #     print("Testing with 10 papers, 7 reviewers 25% conflicts")
    #     self._test_matcher(5, 10, 7, conflict_percentage = 0.25, paper_min_reviewers = 2, reviewer_max_papers = 3)
    #     config_stat = self.conf.get_config_note_status()
    #     assert config_stat == Configuration.STATUS_COMPLETE, "Failure: Config status is {}".format(config_stat)
    #     num_assign_notes = self.conf.get_num_assignment_notes()
    #     assert num_assign_notes == self.num_papers, "Number of assignments {} is not same as number of papers {}".format(num_assign_notes, self.num_papers)
    #
    # def test6_10papers_7reviewers_100_neg_constraints (self):
    #     if not self._should_run(6):
    #         return
    #     print("Testing with 10 papers, 7 reviewers 100% negatively constrained")
    #     self._test_matcher(6, 10, 7, conflict_percentage = 0, paper_min_reviewers = 2, reviewer_max_papers = 3, negative_constraint_percentage = 1)
    #     config_stat = self.conf.get_config_note_status()
    #     assert config_stat == Configuration.STATUS_NO_SOLUTION, "Failure: Config status is {}".format(config_stat)
    #
    # def test7_10papers_7reviewers_10_neg_constraints (self):
    #     if not self._should_run(7):
    #         return
    #     print("Testing with 10 papers, 7 reviewers 10% negatively constrained")
    #     self._test_matcher(7, 10, 7, conflict_percentage = 0, paper_min_reviewers = 2, reviewer_max_papers = 3, negative_constraint_percentage = 0.1)
    #     config_stat = self.conf.get_config_note_status()
    #     assert config_stat == Configuration.STATUS_COMPLETE, "Failure: Config status is {}".format(config_stat)
    #     num_assign_notes = self.conf.get_num_assignment_notes()
    #     assert num_assign_notes == self.num_papers, "Number of assignments {} is not same as number of papers {}".format(num_assign_notes, self.num_papers)
    #
    #
    # # 50% of the paper-reviewer combinations are vetoed and it still finds a match, but it does
    # # find a relatively high-cost one (cost = -3246, whereas the cost of the unconstrained match is -4397)
    # def test8_10papers_7reviewers_50_neg_constraints (self):
    #     if not self._should_run(8):
    #         return
    #     print("Testing with 10 papers, 7 reviewers 50% negatively constrained")
    #     self._test_matcher(8, 10, 7, conflict_percentage = 0, paper_min_reviewers = 2, reviewer_max_papers = 3, negative_constraint_percentage = 0.5)
    #     config_stat = self.conf.get_config_note_status()
    #     assert config_stat == Configuration.STATUS_COMPLETE, "Failure: Config status is {}".format(config_stat)
    #     num_assign_notes = self.conf.get_num_assignment_notes()
    #     assert num_assign_notes == self.num_papers, "Number of assignments {} is not same as number of papers {}".format(num_assign_notes, self.num_papers)
    #
    # def test9_10papers_7reviewers_70_neg_constraints (self):
    #     if not self._should_run(9):
    #         return
    #     print("Testing with 10 papers, 7 reviewers 70% negatively constrained")
    #     self._test_matcher(9, 10, 7, conflict_percentage = 0, paper_min_reviewers = 2, reviewer_max_papers = 3, negative_constraint_percentage = 0.7)
    #     config_stat = self.conf.get_config_note_status()
    #     assert config_stat == Configuration.STATUS_NO_SOLUTION, "Failure: Config status is {}".format(config_stat)
    #
    # # A random 10% of the paper-reviewer combinations are locked and the cost of the assignment found (-4983) is better than
    # # the cost of the solution found in the fully unconstrained match (-4397)
    # # TODO:  This seems odd.  Why do we get a lower cost solution???
    # def test10_10papers_7reviewers_10_pos_constraints (self):
    #     if not self._should_run(10):
    #         return
    #     print("Testing with 10 papers, 7 reviewers 10% positively constrained")
    #     self._test_matcher(10, 10, 7, conflict_percentage = 0, paper_min_reviewers = 2, reviewer_max_papers = 3, positive_constraint_percentage = 0.1)
    #     config_stat = self.conf.get_config_note_status()
    #     assert config_stat == Configuration.STATUS_COMPLETE, "Failure: Config status is {}".format(config_stat)
    #     num_assign_notes = self.conf.get_num_assignment_notes()
    #     assert num_assign_notes == self.num_papers, "Number of assignments {} is not same as number of papers {}".format(num_assign_notes, self.num_papers)
    #
'''
if __name__ == "__main__":
    unittest.main()