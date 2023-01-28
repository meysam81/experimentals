package main

import (
	"net/http"

	"github.com/labstack/echo/v4"
)

func targets() []map[string]interface{} {
	// 	[
	//   {
	//     "targets": [ "<host>", ... ],
	//     "labels": {
	//       "<labelname>": "<labelvalue>", ...
	//     }
	//   },
	//   ...
	// ]
	return []map[string]interface{}{
		{
			"targets": []string{"localhost:9090"},
			"labels": map[string]string{
				"job": "prometheus",
			},
		},
	}

}

func main() {
	e := echo.New()
	// set log level to debug
	e.Logger.SetLevel(1)
	e.GET("/", func(c echo.Context) error {
		return c.JSON(http.StatusOK, targets())
	})
	e.Logger.Fatal(e.Start(":1323"))
}
