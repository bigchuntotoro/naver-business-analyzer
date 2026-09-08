import os
from typing import Optional
from urllib.parse import unquote

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv


# =========================================================
# 환경변수
# =========================================================

load_dotenv()


DEFAULT_API_URL = (
    "https://apis.data.go.kr/"
    "1741000/StanReginCd/getStanReginCdList"
)


API_URL = os.getenv(
    "LEGAL_DONG_API_URL",
    DEFAULT_API_URL
)


class LegalDongAPI:

    def __init__(self):

        # -------------------------------------------------
        # 공공데이터포털 서비스 키
        # -------------------------------------------------

        self.service_key = os.getenv(
            "DATA_GO_KR_SERVICE_KEY"
        )

        if not self.service_key:

            raise ValueError(
                "DATA_GO_KR_SERVICE_KEY가 설정되지 않았습니다.\n"
                ".env 파일을 확인해주세요."
            )

        # -------------------------------------------------
        # Encoding 인증키가 들어온 경우 Decode
        #
        # 예:
        # %2F -> /
        # %3D -> =
        #
        # requests가 다시 URL Encoding 하므로
        # 여기서 한 번 복원해준다.
        # -------------------------------------------------

        self.service_key = unquote(
            self.service_key.strip()
        )

    # =====================================================
    # API 호출
    # =====================================================

    def _request(
        self,
        keyword: str = "",
        page_no: int = 1,
        num_of_rows: int = 1000
    ) -> pd.DataFrame:

        params = {
            "ServiceKey": self.service_key,
            "type": "json",
            "pageNo": page_no,
            "numOfRows": num_of_rows,
            "flag": "Y",
        }

        # -------------------------------------------------
        # 주소 검색
        # -------------------------------------------------

        if keyword:

            params["locatadd_nm"] = keyword

        try:

            response = requests.get(
                API_URL,
                params=params,
                timeout=30
            )

        except requests.RequestException as e:

            raise RuntimeError(
                "법정동 API 네트워크 호출에 실패했습니다.\n\n"
                f"{e}"
            ) from e

        # -------------------------------------------------
        # HTTP 오류
        # -------------------------------------------------

        if response.status_code != 200:

            # 인증키 자체는 오류 메시지에 노출하지 않는다.
            raise RuntimeError(
                "법정동 API 호출에 실패했습니다.\n\n"
                f"HTTP 상태코드: {response.status_code}\n"
                f"응답 내용: {response.text[:1000]}"
            )

        # -------------------------------------------------
        # JSON 변환
        # -------------------------------------------------

        try:

            data = response.json()

        except ValueError as e:

            raise RuntimeError(
                "법정동 API가 JSON 형식의 응답을 "
                "반환하지 않았습니다.\n\n"
                f"응답 내용:\n{response.text[:1000]}"
            ) from e

        # =================================================
        # API 오류 응답
        # =================================================

        if "OpenAPI_ServiceResponse" in data:

            error_data = data[
                "OpenAPI_ServiceResponse"
            ]

            header = error_data.get(
                "cmmMsgHeader",
                {}
            )

            reason_code = header.get(
                "returnReasonCode",
                ""
            )

            auth_msg = header.get(
                "returnAuthMsg",
                ""
            )

            raise RuntimeError(
                "공공데이터 API 오류\n"
                f"코드: {reason_code}\n"
                f"메시지: {auth_msg}"
            )

        # =================================================
        # 정상 응답
        # =================================================

        stan_regin_cd = data.get(
            "StanReginCd"
        )

        if not stan_regin_cd:

            return pd.DataFrame()

        # -------------------------------------------------
        # API 구조
        #
        # StanReginCd
        #   ├── head
        #   └── row
        # -------------------------------------------------

        rows = []

        if len(stan_regin_cd) > 1:

            rows = stan_regin_cd[1].get(
                "row",
                []
            )

        if isinstance(rows, dict):

            rows = [rows]

        if not rows:

            return pd.DataFrame()

        df = pd.DataFrame(rows)

        return self._normalize(df)

    # =====================================================
    # 데이터 정규화
    # =====================================================

    @staticmethod
    def _normalize(
        df: pd.DataFrame
    ) -> pd.DataFrame:

        # -------------------------------------------------
        # 법정동 코드
        # -------------------------------------------------

        if "region_cd" in df.columns:

            df["region_cd"] = (
                df["region_cd"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

        # -------------------------------------------------
        # 주소
        # -------------------------------------------------

        if "locatadd_nm" in df.columns:

            df["locatadd_nm"] = (
                df["locatadd_nm"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

        return df

    # =====================================================
    # 주소 파싱
    # =====================================================

    @staticmethod
    def _parse_address(
        address: str
    ) -> dict:

        if not address:

            return {
                "sido": "",
                "sigungu": "",
                "dong": "",
                "ri": "",
            }

        parts = address.split()

        return {
            "sido": parts[0]
            if len(parts) >= 1
            else "",

            "sigungu": parts[1]
            if len(parts) >= 2
            else "",

            "dong": parts[2]
            if len(parts) >= 3
            else "",

            "ri": parts[3]
            if len(parts) >= 4
            else "",
        }

    # =====================================================
    # 시/도 목록
    # =====================================================

    @st.cache_data(
        ttl=60 * 60 * 24,
        show_spinner=False
    )
    def get_sido_list(
        _self
    ):

        # -------------------------------------------------
        # 전국 데이터를 한 번에 1000개 가져오는 방식 대신
        # API에서 주요 광역자치단체를 검색한다.
        #
        # 법정동 데이터는 실제 코드 시스템에서
        # 지속적으로 변경될 수 있으므로
        # 하드코딩보다 API 기반으로 처리한다.
        # -------------------------------------------------

        sido_keywords = [
            "서울특별시",
            "부산광역시",
            "대구광역시",
            "인천광역시",
            "광주광역시",
            "대전광역시",
            "울산광역시",
            "세종특별자치시",
            "경기도",
            "강원특별자치도",
            "충청북도",
            "충청남도",
            "전북특별자치도",
            "전라남도",
            "경상북도",
            "경상남도",
            "제주특별자치도",
        ]

        result = []

        for sido in sido_keywords:

            try:

                df = _self._request(
                    keyword=sido,
                    page_no=1,
                    num_of_rows=1
                )

                if not df.empty:

                    result.append(sido)

            except RuntimeError:

                continue

        return result

    # =====================================================
    # 시/군/구 목록
    # =====================================================

    @st.cache_data(
        ttl=60 * 60 * 24,
        show_spinner=False
    )
    def get_sigungu_list(
        _self,
        sido: str
    ):

        if not sido:

            return []

        df = _self._request(
            keyword=sido,
            page_no=1,
            num_of_rows=1000
        )

        if df.empty:

            return []

        result = []

        for address in df["locatadd_nm"]:

            parsed = _self._parse_address(
                address
            )

            if parsed["sido"] == sido:

                sigungu = parsed["sigungu"]

                if sigungu:

                    result.append(sigungu)

        return sorted(
            list(set(result))
        )

    # =====================================================
    # 읍/면/동 목록
    # =====================================================

    @st.cache_data(
        ttl=60 * 60 * 24,
        show_spinner=False
    )
    def get_dong_list(
        _self,
        sido: str,
        sigungu: str
    ):

        if not sido or not sigungu:

            return []

        keyword = (
            f"{sido} "
            f"{sigungu}"
        )

        df = _self._request(
            keyword=keyword,
            page_no=1,
            num_of_rows=1000
        )

        if df.empty:

            return []

        result = []

        for address in df["locatadd_nm"]:

            parsed = _self._parse_address(
                address
            )

            if (
                parsed["sido"] == sido
                and
                parsed["sigungu"] == sigungu
            ):

                dong = parsed["dong"]

                if dong:

                    result.append(dong)

        return sorted(
            list(set(result))
        )

    # =====================================================
    # 법정동 정보
    # =====================================================

    @st.cache_data(
        ttl=60 * 60 * 24,
        show_spinner=False
    )
    def get_dong_info(
        _self,
        sido: str,
        sigungu: str,
        dong: str
    ) -> Optional[dict]:

        if (
            not sido
            or not sigungu
            or not dong
        ):

            return None

        keyword = (
            f"{sido} "
            f"{sigungu} "
            f"{dong}"
        )

        df = _self._request(
            keyword=keyword,
            page_no=1,
            num_of_rows=100
        )

        if df.empty:

            return None

        # -------------------------------------------------
        # 정확히 일치하는 법정동 검색
        # -------------------------------------------------

        for _, row in df.iterrows():

            address = str(
                row.get(
                    "locatadd_nm",
                    ""
                )
            ).strip()

            if not address:

                continue

            parsed = _self._parse_address(
                address
            )

            if (
                parsed["sido"] == sido
                and
                parsed["sigungu"] == sigungu
                and
                parsed["dong"] == dong
            ):

                region_cd = str(
                    row.get(
                        "region_cd",
                        ""
                    )
                ).strip()

                return {
                    "법정동코드": region_cd,
                    "시도명": parsed["sido"],
                    "시군구명": parsed["sigungu"],
                    "읍면동명": parsed["dong"],
                    "리명": parsed["ri"],
                    "주소": address,
                }

        return None

    # =====================================================
    # 법정동 코드
    # =====================================================

    def get_dong_code(
        self,
        sido: str,
        sigungu: str,
        dong: str
    ) -> Optional[str]:

        info = self.get_dong_info(
            sido,
            sigungu,
            dong
        )

        if not info:

            return None

        return info.get(
            "법정동코드"
        )