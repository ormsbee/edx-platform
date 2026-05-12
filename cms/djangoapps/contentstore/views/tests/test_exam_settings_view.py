"""
Exam Settings View Tests
"""
import ddt
from django.conf import settings
from django.test.utils import override_settings
from edx_toggles.toggles.testutils import override_waffle_flag

from cms.djangoapps.contentstore import toggles
from cms.djangoapps.contentstore.tests.utils import CourseTestCase
from cms.djangoapps.contentstore.utils import reverse_course_url
from common.djangoapps.util.testing import UrlResetMixin


@ddt.ddt
@override_settings(
    FEATURES={
        **settings.FEATURES,
        "CERTIFICATES_HTML_VIEW": True,
        "ENABLE_PROCTORED_EXAMS": True,
    },
)
@override_waffle_flag(toggles.LEGACY_STUDIO_CONFIGURATIONS, True)
@override_settings(COURSE_AUTHORING_MICROFRONTEND_URL='https://mfe.example')
class TestExamSettingsView(CourseTestCase, UrlResetMixin):
    """
    Unit tests for the exam settings view.
    """
    def setUp(self):
        """
        Set up the for the exam settings view tests.
        """
        super().setUp()
        self.reset_urls()

    @override_waffle_flag(toggles.LEGACY_STUDIO_EXAM_SETTINGS, True)
    @ddt.data(
        "group_configurations_list_handler",
    )
    def test_view_without_exam_settings_enabled(self, handler):
        """
        Tests pages should not have `Exam Settings` item
        if course does not have the Exam Settings view enabled.
        """
        outline_url = reverse_course_url(handler, self.course.id)
        resp = self.client.get(outline_url, HTTP_ACCEPT='text/html')
        self.assertEqual(resp.status_code, 200)  # noqa: PT009
        self.assertNotContains(resp, 'Proctored Exam Settings')

    @ddt.data(
        "group_configurations_list_handler",
    )
    def test_view_with_exam_settings_enabled(self, handler):
        """
        Tests pages should have `Exam Settings` item
        if course does have Exam Settings view enabled.
        """
        outline_url = reverse_course_url(handler, self.course.id)
        resp = self.client.get(outline_url, HTTP_ACCEPT='text/html')
        self.assertEqual(resp.status_code, 200)  # noqa: PT009
        self.assertContains(resp, 'Proctored Exam Settings')

    def test_grading_handler_redirects_to_mfe(self):
        """grading_handler redirects to the authoring MFE."""
        url = reverse_course_url('grading_handler', self.course.id)
        resp = self.client.get(url, HTTP_ACCEPT='text/html')
        self.assertEqual(resp.status_code, 302)  # noqa: PT009

    def test_settings_handler_redirects_to_mfe(self):
        """settings_handler (schedule & details) redirects to the authoring MFE."""
        url = reverse_course_url('settings_handler', self.course.id)
        resp = self.client.get(url, HTTP_ACCEPT='text/html')
        self.assertEqual(resp.status_code, 302)  # noqa: PT009

    def test_certificates_list_handler_redirects_to_mfe(self):
        """certificates_list_handler redirects to the authoring MFE."""
        url = reverse_course_url('certificates_list_handler', self.course.id)
        resp = self.client.get(url, HTTP_ACCEPT='text/html')
        self.assertEqual(resp.status_code, 302)  # noqa: PT009

    def test_advanced_settings_handler_redirects_to_mfe(self):
        """advanced_settings_handler redirects to the authoring MFE."""
        url = reverse_course_url('advanced_settings_handler', self.course.id)
        resp = self.client.get(url, HTTP_ACCEPT='text/html')
        self.assertEqual(resp.status_code, 302)  # noqa: PT009
