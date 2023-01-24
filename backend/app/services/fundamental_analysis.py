import base64
from bs4 import BeautifulSoup
from copy import deepcopy
from datetime import datetime
from dateutil.parser import parse
from io import BytesIO
from matplotlib.figure import Figure
import pandas as pd
import re


class FundamentalAnalysis:
    def __init__(self):
        self.stat_types = [
            'balance',
            # 'operation',
            'income/loss/comprehensive_lo',
            # 'stockholder/redeemable/interests/equity',
            'flow'
        ]

    def scrape(self, urls: list):
        return {
            i: self._find_table_by_type(
                table=BeautifulSoup(
                    open(n, "r", encoding='utf-8').read(),
                    "lxml"),
            )
            for i, n in enumerate(urls)
        }

    def _clean_table(self, table, scale):
        stmt_df_by_stmt_type = deepcopy(table)
        stmt_df_by_stmt_type.rename(
            columns={stmt_df_by_stmt_type.columns[0]: 'index'},
            inplace=True,
        )

        for i, ind in enumerate(stmt_df_by_stmt_type['index']):
            if ind == 'Basic':
                stmt_df_by_stmt_type[
                    "index"][i] = f'{stmt_df_by_stmt_type["index"][i-1]} Basic'
                stmt_df_by_stmt_type[
                    "index"][i+1] = f'{stmt_df_by_stmt_type["index"][i-1]} Diluted'

            stmt_df_by_stmt_type['index'][i] = ' '.join(
                re.sub(r"[\(\[].*?[\)\]]", "", ind).replace(':', '')
                .replace('loss', 'income').split()
            )

        stmt_df_by_stmt_type.set_index('index', inplace=True)
        good_col = [
            i
            for i in range(1, len(stmt_df_by_stmt_type.iloc[0]))
            if (
                ((stmt_df_by_stmt_type.iloc[:, i].values == '').sum()
                    / len(stmt_df_by_stmt_type.iloc[:, i]))*100 <= 40
                and any(
                    x not in stmt_df_by_stmt_type.index.values
                    for x in list(
                        filter(None, stmt_df_by_stmt_type.iloc[:, i])
                    )
                )
                and all(
                    x not in stmt_df_by_stmt_type.iloc[:, i].values
                    for x in ['$', ')'])
            )
        ]
        stmt_df_by_stmt_type = stmt_df_by_stmt_type.iloc[:, good_col]

        good_rows = [
            n
            for n, val in enumerate(stmt_df_by_stmt_type.index.values)
            if val != ''
        ]
        new_header_row = int(good_rows[0])-1
        new_head = [
            stmt_df_by_stmt_type.iloc[:new_header_row+1, i].sum()
            for i in range(len(stmt_df_by_stmt_type.iloc[new_header_row]))
        ]
        stmt_df_by_stmt_type.columns = new_head
        stmt_df_by_stmt_type.iloc[new_header_row] = ''
        stmt_df_by_stmt_type = stmt_df_by_stmt_type.iloc[good_rows]

        replacers = {
            ',': '',
            '—': '',
            r'\(': '-',
        }
        stmt_df_by_stmt_type.replace(replacers, regex=True, inplace=True)

        for col in stmt_df_by_stmt_type.columns:
            stmt_df_by_stmt_type[col] = pd.to_numeric(
                stmt_df_by_stmt_type[col]
            )
        stmt_df_by_stmt_type.fillna(0.0, inplace=True)

        if 'thousand' in scale:
            stmt_df_by_stmt_type = (stmt_df_by_stmt_type/1000).round(2)

        return stmt_df_by_stmt_type

    def _find_table_by_type(self, table) -> dict:
        ''' Find tables by statement type. '''
        quarterly_df = {}
        for stattype in self.stat_types:
            patterns = stattype.split('/')

            if len(patterns) > 1:
                found_p_table = False
                for pattern in patterns:
                    if not found_p_table:
                        stmt_html = table.find(
                            "p",
                            {'id': re.compile(pattern, re.IGNORECASE)},
                        )
                        if stmt_html is not None:
                            found_p_table = True
            else:
                stmt_html = table.find(
                    "p",
                    {'id': re.compile(patterns[0], re.IGNORECASE)},
                )

            try:
                stmt_df = pd.read_html(
                    str(stmt_html.findNext('table')),
                    na_values=' ',
                    keep_default_na=False,
                )
            except AttributeError:
                # Change in html tags and format in 2020.
                if len(patterns) > 1:
                    found_a_table = False
                    for pattern in patterns:
                        if not found_a_table:
                            stmt_html = table.find(
                                "a",
                                {'name': re.compile(pattern, re.IGNORECASE)},
                            )
                            if stmt_html is not None:
                                found_a_table = True
                else:
                    stmt_html = table.find(
                        "a",
                        {'name': re.compile(patterns[0], re.IGNORECASE)},
                    )
                stmt_df = pd.read_html(
                    str(stmt_html.findNext('table')),
                    na_values=' ',
                    keep_default_na=False,
                )

            try:
                stmt_scale = stmt_html.findNext(
                    'span',
                    text=re.compile(r'^\(in', re.IGNORECASE),
                ).text
            except:
                stmt_scale = stmt_html.findNext(
                    'p',
                    text=re.compile(r'^\(in', re.IGNORECASE),
                ).text

            quarterly_df[stattype] = self._clean_table(
                table=stmt_df[0],
                scale=stmt_scale,
            )
        return quarterly_df

    def _generate_clean_statements(self, df_data):
        ''' Clean data, transpose, and re-index table. '''
        # Sort the header if the header is a date:
        try:
            new_header = [
                datetime.strptime(
                    header.replace(u'\xa0', u' '),
                    '%B %d,%Y'
                ).date()
                for header in df_data.columns
            ]
            df_data.columns = new_header
        except:
            pass

        df_data = df_data.loc[:, ~df_data.columns.duplicated()].copy()
        df_data = df_data.reindex(sorted(df_data.columns), axis=1)
        t_data_df = df_data.transpose()
        return t_data_df

    def generate_all_state_figs(self, all_statements) -> dict:
        ''' Combine all tables of a statement type and return plotted data. '''
        all_results = {
            stype: pd.concat(
                [
                    i[k]
                    for i in all_statements.values()
                    for k in i
                    if stype == k
                ],
                axis=1,
            )
            for stype in self.stat_types
        }

        return {
            stat_type: self._statement_figures(
                all_statements=all_results,
                stat_type=stat_type,
                fig_size=len(self.stat_types),
            )
            for stat_type in self.stat_types
        }

    def _statement_figures(
        self,
        all_statements,
        stat_type: str,
        fig_size: int,
    ) -> dict:
        ''' Generate all figures for each type of statement. '''
        fig_data = {}
        if stat_type == 'balance':
            balance_df = self._generate_clean_statements(
                all_statements[stat_type]
            )

            total_balance_stmts = [
                i
                for i, col in enumerate(balance_df, start=1)
                if 'total' in col.lower()
            ]
            total_balance_stmts.insert(0, 0)

            bal_stmt_col = [
                list(
                    balance_df.iloc[
                        :,
                        total_balance_stmts[i]:total_balance_stmts[i+1]
                    ].columns)
                for i in range(len(total_balance_stmts)-1)
            ]

            fig = Figure(figsize=(40, 40))
            for i in range(len(bal_stmt_col)):
                ax = fig.add_subplot(4, 2, i+1)
                ax.plot(
                    balance_df[bal_stmt_col[i][:-1]],
                    '-o',
                    label=bal_stmt_col[i][:-1],
                    linewidth=0.75,
                )
                ax.plot(
                    balance_df[bal_stmt_col[i][-1]],
                    '-o',
                    label=bal_stmt_col[i][-1],
                    linewidth=3,
                )
                ax.legend()

            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight')
            fig_data[stat_type] = base64.b64encode(
                buf.getbuffer()
            ).decode("ascii")

        if stat_type in ['income/loss/comprehensive_lo', 'flow']:
            income_loss_df = self._generate_clean_statements(
                all_statements[stat_type]
            )
            income_loss_df.fillna(0.0, inplace=True)

            empty_rows = [
                n
                for n in range(len(income_loss_df.index.values))
                if income_loss_df.index.values[n] == ''
            ]
            income_loss_df.drop(
                income_loss_df.index[empty_rows],
                inplace=True,
            )

            empty_col = [
                i
                for i in range(len(income_loss_df.iloc[0]))
                if (
                    (income_loss_df.iloc[:, i].values == 0.0).sum()
                    / len(income_loss_df.iloc[:, i])
                ) == 1
            ]
            empty_col.insert(0, -1)
            empty_col.append(len(income_loss_df.iloc[0])-2)
            empty_col = list(set(empty_col))

            income_stmt_col = [
                list(
                    income_loss_df.iloc[
                        :,
                        empty_col[i]+1:empty_col[i+1]
                    ].columns
                )
                for i in range(len(empty_col)-1)
            ]

            striped_index_dates = [
                parse(dtstr.replace(',', ' '), fuzzy_with_tokens=True)[0]
                if dtstr != '' else ''
                for dtstr in income_loss_df.index
            ]
            income_loss_df['dates'] = striped_index_dates

            income_index = {
                i: [
                    ind
                    for ind in income_loss_df.index
                    if i in ind.lower()
                ]
                for i in ['three', 'six', 'nine']
            }

            fig = Figure(figsize=(20 * len(income_stmt_col), 50))
            count = 1
            for k in ['three', 'six', 'nine']:
                reduced_df = income_loss_df.loc[income_index[k]]
                ordered_red_df = reduced_df.sort_values(by=['dates'])
                ordered_red_df.set_index('dates', inplace=True)

                for i in range(len(income_stmt_col)):
                    ax = fig.add_subplot(3, len(income_stmt_col), count)
                    ax.plot(
                        ordered_red_df[income_stmt_col[i]],
                        '-o',
                        label=income_stmt_col[i],
                        linewidth=0.75,
                    )
                    count += 1
                    ax.legend()
                    # ax.set_title(income_stmt_col[i])

            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight')
            fig_data[stat_type] = base64.b64encode(
                buf.getbuffer()
            ).decode("ascii")

        return fig_data
